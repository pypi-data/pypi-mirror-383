"""SQL Agent evaluator core class"""

import os
import json
import re
import requests
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import pymysql
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

from .agent import SQLAgent
from .result import EvaluationResult


class SQLEvaluator:
    """SQL Agent Evaluator"""
    
    def __init__(self, 
                 database_config: Optional[Dict[str, Any]] = None,
                 llm_config: Optional[Dict[str, Any]] = None,
                 datasets_path: str = "datasets",
                 prompts_path: str = "prompts",
                 env_file: Optional[str] = None):
        """Initialize evaluator
        
        Args:
            database_config: Database configuration, if None then read from environment variables
            llm_config: LLM configuration, if None then read from environment variables
            datasets_path: Dataset directory path
            prompts_path: Template directory path
            env_file: .env file path (optional)
        """
        # Load environment variables
        if env_file:
            # User specified explicit env file
            load_dotenv(env_file)
        else:
            # Auto-discover .env file in multiple locations:
            # 1. Current working directory (.env)
            # 2. Current working directory (config/.env) - for project layout
            # 3. Home directory (~/.sqleval.env) - for global config
            env_locations = [
                '.env',                                    # CWD
                'config/.env',                            # CWD/config
                str(Path.home() / '.sqleval.env')        # Home directory
            ]
            
            loaded = False
            for env_path in env_locations:
                if Path(env_path).exists():
                    load_dotenv(env_path)
                    loaded = True
                    logging.debug(f"Loaded environment from: {env_path}")
                    break
            
            if not loaded:
                logging.debug("No .env file found in default locations")
        
        self.datasets_path = Path(datasets_path)
        self.prompts_path = Path(prompts_path)
        
        # Database configuration
        if database_config:
            self.db_config = database_config
        else:
            # Read from environment variables (no defaults - must be explicitly set)
            required_db_vars = ['DATABASE_HOST', 'DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_NAME']
            missing_vars = [var for var in required_db_vars if not os.getenv(var)]
            
            if missing_vars:
                raise ValueError(
                    f"Missing required database environment variables: {', '.join(missing_vars)}\n"
                    f"Please set them in your .env file or pass database_config to SQLEvaluator()"
                )
            
            self.db_config = {
                'host': os.getenv('DATABASE_HOST'),
                'port': int(os.getenv('DATABASE_PORT', '3306')),
                'user': os.getenv('DATABASE_USER'),
                'password': os.getenv('DATABASE_PASSWORD'),
                'database': os.getenv('DATABASE_NAME')
            }
        
        # LLM configuration
        if llm_config:
            self.llm_config = llm_config
        else:
            # Read from environment variables (no defaults - must be explicitly set)
            if not os.getenv('EVAL_LLM_API_KEY'):
                raise ValueError(
                    "Missing required LLM environment variable: EVAL_LLM_API_KEY\n"
                    "Please set it in your .env file or pass llm_config to SQLEvaluator()"
                )
            
            self.llm_config = {
                'api_key': os.getenv('EVAL_LLM_API_KEY'),
                'base_url': os.getenv('EVAL_LLM_BASE_URL', 'https://api.openai.com/v1'),
                'model': os.getenv('EVAL_LLM_MODEL', 'gpt-4'),
                'max_tokens': 300,
                'temperature': 0.1
            }
        
        # Template environment
        self.template_env = Environment(loader=FileSystemLoader(self.prompts_path))
        
        # Load dataset weights
        self.dataset_weights = self.load_dataset_weights()
        
        # Print initialization summary
        print("✅ SQLEvaluator initialized")
        print(f"📊 Database: {self.db_config['host']}:{self.db_config['port']}")
        print(f"🤖 LLM: {self.llm_config['model']}")
    
    def validate_configuration(self) -> bool:
        """Validate configuration and environment setup"""
        logging.info("Validating configuration...")
        
        # Check database configuration
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            logging.info("✅ Database connection validated")
        except Exception as e:
            logging.error(f"❌ Database connection failed: {e}")
            return False
        
        # Check LLM configuration
        try:
            headers = {
                'Authorization': f'Bearer {self.llm_config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            # Simple test request
            test_data = {
                "model": self.llm_config["model"],
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.llm_config['base_url']}/chat/completions",
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info("✅ LLM API connection validated")
            else:
                logging.error(f"❌ LLM API failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ LLM API connection failed: {e}")
            return False
        
        # Check datasets
        datasets = self.scan_datasets()
        if not datasets:
            logging.error("❌ No datasets found")
            return False
        
        logging.info(f"✅ Found {len(datasets)} datasets")
        
        # Check prompts
        if not self.prompts_path.exists():
            logging.error(f"❌ Prompts directory not found: {self.prompts_path}")
            return False
        
        logging.info("✅ Configuration validation completed successfully")
        return True
    
    def _check_dataset_tables_exist(self, connection, dataset_name: str) -> bool:
        """Check if tables for a dataset already exist in the database
        
        Args:
            connection: Database connection
            dataset_name: Name of the dataset to check
            
        Returns:
            bool: True if dataset tables exist, False otherwise
        """
        try:
            cursor = connection.cursor()
            
            # Get table names from the dataset's schema file
            dataset_dir = self.datasets_path / dataset_name
            schema_file = dataset_dir / "schema.sql"
            
            if not schema_file.exists():
                return False
            
            # Read schema file and extract table names
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            
            # Extract table names using regex: CREATE TABLE table_name
            table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?'
            tables = re.findall(table_pattern, schema_content, re.IGNORECASE)
            
            if not tables:
                return False
            
            # Check if all tables exist
            for table in tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if not cursor.fetchone():
                    cursor.close()
                    return False
            
            cursor.close()
            return True
            
        except Exception as e:
            logging.debug(f"Error checking tables for dataset {dataset_name}: {e}")
            return False
    
    def load_dataset_weights(self) -> Dict[str, int]:
        """Load dataset weights from meta.txt"""
        meta_file = self.datasets_path / "meta.txt"
        weights = {}
        
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                dataset_name, weight = line.split('=', 1)
                                weights[dataset_name.strip()] = int(weight.strip())
                logging.info(f"Loaded dataset weights: {weights}")
            except Exception as e:
                logging.error(f"Failed to load dataset weights: {e}")
                weights = {}
        else:
            logging.warning(f"Meta file not found: {meta_file}")
            weights = {}
        
        return weights
    
    def prepare_environment(self, datasets: Optional[List[str]] = None):
        """Prepare evaluation environment by setting up database and datasets
        
        This method can be called independently to set up the environment before evaluation.
        Useful when you want to:
        - Set up environment once and run multiple evaluations
        - Inspect the database setup before evaluation
        - Control environment lifecycle manually (setup → evaluate → cleanup)
        
        Args:
            datasets: Optional list of specific dataset names to prepare.
                     If None, prepares all datasets with weight > 0.
            
        Returns:
            dict: Environment info including datasets and connection
            
        Example:
            >>> # Manual control
            >>> evaluator.prepare_environment()
            >>> evaluator.evaluate(agent)
            >>> evaluator.clean_environment()
            >>> evaluator.close_connection()
            
            >>> # Or prepare specific datasets
            >>> evaluator.prepare_environment(datasets=['example'])
        """
        # Scan and filter datasets
        available_datasets, conn = self._prepare_evaluation_environment(datasets)
        if not available_datasets or not conn:
            return {'datasets': [], 'connection': None}
        
        # Set up each dataset
        print("🔧 Setting up database environments...")
        for dataset in available_datasets:
            print(f"  ⚙️  Setting up dataset: {dataset['name']}")
            self.setup_database_with_connection(
                conn, 
                dataset['schema_file'], 
                dataset['data_file']
            )
        
        print("✅ All database environments setup completed")
        
        # Store connection and datasets for later use
        self._active_connection = conn
        self._active_datasets = available_datasets
        
        return {
            'datasets': [d['name'] for d in available_datasets],
            'connection': conn,
            'dataset_count': len(available_datasets)
        }
    
    def clean_environment(self, datasets: Optional[List[str]] = None):
        """Clean up database environments
        
        This method can be called independently to clean up after evaluation.
        If datasets parameter is provided, only those datasets will be cleaned.
        Otherwise, all active datasets will be cleaned.
        
        Args:
            datasets: Optional list of specific dataset names to clean.
                     If None, cleans all active datasets.
            
        Example:
            >>> evaluator.prepare_environment()
            >>> evaluator.evaluate(agent)
            >>> evaluator.clean_environment()
            
            >>> # Or clean specific datasets
            >>> evaluator.clean_environment(datasets=['example'])
        """
        if not hasattr(self, '_active_connection') or self._active_connection is None:
            print("⚠️  No active database connection found. Did you call prepare_environment()?")
            return
        
        datasets_to_clean = self._active_datasets if hasattr(self, '_active_datasets') else []
        
        # Filter if specific datasets requested
        if datasets:
            datasets_to_clean = [d for d in datasets_to_clean if d['name'] in datasets]
        
        if not datasets_to_clean:
            print("⚠️  No datasets to clean")
            return
        
        print("🧹 Cleaning up database environments...")
        for dataset in datasets_to_clean:
            print(f"  🗑️  Cleaning dataset: {dataset['name']}")
            self.cleanup_database_environment(
                self._active_connection,
                dataset['clean_file']
            )
        
        print("✅ Database environments cleaned up")
        
        # Automatically close connection after cleanup
        if hasattr(self, '_active_connection') and self._active_connection:
            self._active_connection.close()
            print("🔌 Database connection closed")
            self._active_connection = None
            self._active_datasets = []
    
    def _prepare_evaluation_environment(self, datasets: Optional[List[str]] = None) -> tuple:
        """Internal method: Prepare evaluation environment
        
        This is used internally by evaluate() method for automatic environment management.
        For manual environment control, use prepare_environment() instead.
        
        Returns:
            tuple: (available_datasets, database_connection)
        """
        # Scan available datasets
        print("📂 Scanning available datasets...")
        available_datasets = self.scan_datasets()
        
        if not available_datasets:
            print("❌ No available datasets found")
            logging.error("No available datasets found")
            return [], None
        
        # Filter datasets
        if datasets:
            available_datasets = [d for d in available_datasets if d['name'] in datasets]
        
        # Skip datasets with weight 0 unless explicitly specified
        if not datasets:  # Only skip when evaluating all datasets
            available_datasets = [d for d in available_datasets if self.dataset_weights.get(d['name'], 0) > 0]
        
        print(f"📊 Found {len(available_datasets)} datasets: {[d['name'] for d in available_datasets]}")
        
        # Establish database connection
        print("🔗 Establishing database connection...")
        logging.info("Establishing database connection...")
        conn = pymysql.connect(**self.db_config)
        print(f"✅ Database connection successful: {self.db_config['host']}:{self.db_config['port']}")
        logging.info(f"Database connection successful: {self.db_config['host']}:{self.db_config['port']}")
        
        return available_datasets, conn
    
    async def _evaluate_agent_on_dataset(self, agent: SQLAgent, questions: List[Dict[str, str]], 
                                 dataset_name: str) -> List[Dict[str, Any]]:
        """Evaluate a single agent on a single dataset - common logic
        
        Args:
            agent: SQL Agent to evaluate
            questions: List of questions for this dataset
            dataset_name: Name of the dataset
            
        Returns:
            List of evaluation results for this agent on this dataset
        """
        results = []
        question_count = len(questions)
        
        # Run evaluation
        for i, q in enumerate(questions, 1):
            print(f"    🔍 [{i}/{question_count}] Processing question: {q['title'][:30]}...")
            
            # Agent processing
            print(f"      🤖 Agent analyzing...")
            agent_result = agent.optimize(q['sql'])
            
            # LLM scoring
            print(f"      🧠 LLM scoring...")
            eval_result = await self.evaluate_with_llm(
                agent_result, q['expected'], q['scoring_rules'], q['sql']
            )
            score = eval_result['score']
            
            # Collect results
            results.append({
                'dataset': dataset_name,
                'question_id': i,
                'title': q['title'],
                'sql': q['sql'],
                'expected': q['expected'],
                'agent_optimization': agent_result,
                'agent_reasoning': agent_result,
                'score': score,
                'explanation': eval_result['explanation'].strip()
            })
            
            print(f"      ✅ Complete! Score: {score}/10")
        
        return results
    
    def scan_datasets(self) -> List[Dict[str, str]]:
        """Scan available datasets"""
        datasets = []
        
        if not self.datasets_path.exists():
            logging.error(f"Dataset directory does not exist: {self.datasets_path}")
            return datasets
        
        # Iterate through all subdirectories in dataset directory
        for dataset in self.datasets_path.iterdir():
            if dataset.is_dir():
                dataset_name = dataset.name
                schema_file = dataset / "schema.sql"
                data_file = dataset / "data.sql"
                questions_file = dataset / "questions.md"
                clean_file = dataset / "clean.sql"
                
                # Check if required files exist
                if questions_file.exists():
                    datasets.append({
                        "name": dataset_name,
                        "schema_file": str(schema_file),
                        "data_file": str(data_file),
                        "questions_file": str(questions_file),
                        "clean_file": str(clean_file)
                    })
                    logging.info(f"Found dataset: {dataset_name}")
                else:
                    logging.warning(f"Dataset {dataset_name} missing questions.md file")
        
        return datasets
    
    def parse_questions(self, md_file: str) -> List[Dict[str, str]]:
        """Parse questions.md file"""
        logging.info(f"Parsing question file: {md_file}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Support both Chinese and English formats
        sections = []
        if '## Question' in content:
            sections = content.split('## Question')[1:]
        else:
            # Fallback: split by any ## pattern
            sections = re.split(r'## [^\n]+', content)[1:]
        
        questions = []
        
        for section in sections:
            # Extract title
            title_match = re.search(r'(\d+)[：:]\s*([^\n]+)', section)
            title = title_match.group(2) if title_match else "Untitled Question"
            
            # Extract SQL
            sql_match = re.search(r'\*\*SQL:\*\*\s*`([^`]+)`', section)
            if not sql_match:
                sql_match = re.search(r'\*\*SQL\*\*:\s*`([^`]+)`', section)
            sql = sql_match.group(1) if sql_match else ""
            
            # Extract expected result
            result_match = re.search(r'\*\*Expected Result:\*\*\s*([^\n]+)', section)
            expected = result_match.group(1) if result_match else ""
            
            # Extract scoring rules
            scoring_match = re.search(r'\*\*Scoring:\*\*.*?(.*?)(?=---|$)', section, re.DOTALL)
            scoring_rules = scoring_match.group(1).strip() if scoring_match else ""
            
            if sql:
                questions.append({
                    'title': title,
                    'sql': sql.strip(),
                    'expected': expected,
                    'scoring_rules': scoring_rules
                })
        
        logging.info(f"Parsed {len(questions)} questions")
        return questions
    
    def setup_database_with_connection(self, conn, schema_file: str, data_file: str):
        """Setup database environment using existing connection"""
        cursor = conn.cursor()
        
        # Execute schema
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
            statements = schema_sql.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    try:
                        cursor.execute(stmt)
                        logging.debug(f"Executing SQL: {stmt[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e) or "Table" in str(e):
                            logging.debug(f"Table already exists, skipping: {stmt[:50]}...")
                        else:
                            logging.error(f"SQL execution failed: {e}")
        
        # Execute data file
        with open(data_file, 'r', encoding='utf-8') as f:
            data_sql = f.read()
            
            # Remove SQL comments (-- style)
            data_sql_cleaned = re.sub(r'--[^\n]*\n', '\n', data_sql)
            
            # Remove DELIMITER commands (MySQL client specific)
            data_sql_cleaned = re.sub(r'DELIMITER\s+\$\$\s*\n', '', data_sql_cleaned)
            data_sql_cleaned = re.sub(r'DELIMITER\s+;\s*\n', '', data_sql_cleaned)
            
            # Extract and execute statements separately
            # Match: SET...;  INSERT...;  DROP PROCEDURE...$$  CREATE PROCEDURE...$$  CALL...;  ANALYZE...;  DROP TABLE...;
            pattern = r'(SET\s+(?:SESSION\s+)?[^;]+;|DROP\s+TABLE[^;]+;|DROP\s+PROCEDURE[^$]*\$\$|CREATE\s+PROCEDURE.*?END\s*\$\$|INSERT\s+(?:IGNORE\s+)?INTO[^;]+;|CALL[^;]+;|ANALYZE[^;]+;|DROP\s+PROCEDURE[^;]+;)'
            
            statements = re.findall(pattern, data_sql_cleaned, re.IGNORECASE | re.DOTALL)
            
            logging.info(f"Found {len(statements)} statements to execute")
            
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt:
                    continue
                
                # Remove $$ terminator if present, replace with nothing
                if stmt.endswith('$$'):
                    stmt = stmt[:-2].strip()
                
                try:
                    cursor.execute(stmt)
                    stmt_preview = stmt[:60].replace('\n', ' ')
                    
                    if stmt.upper().startswith('SET'):
                        logging.debug(f"Set session variable: {stmt_preview}...")
                    elif stmt.upper().startswith('INSERT'):
                        logging.debug(f"Inserted data")
                    elif stmt.upper().startswith('CREATE PROCEDURE'):
                        logging.info(f"Created procedure: {stmt_preview}...")
                    elif stmt.upper().startswith('CALL'):
                        logging.info(f"Executing procedure: {stmt_preview}...")
                    elif stmt.upper().startswith('DROP PROCEDURE') or stmt.upper().startswith('DROP TABLE'):
                        logging.debug(f"Dropped object")
                    elif stmt.upper().startswith('ANALYZE'):
                        logging.info(f"Analyzing table: {stmt_preview}...")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "Duplicate entry" in error_msg:
                        logging.debug("Data already exists, skipping")
                    elif "doesn't exist" in error_msg.lower():
                        logging.debug("Object doesn't exist, skipping")
                    else:
                        # Show full error message for debugging
                        logging.warning(f"SQL execution warning: {error_msg}")
                        logging.debug(f"Failed statement: {stmt[:200]}")
        
        conn.commit()
        cursor.close()
        logging.debug("Database environment setup completed")
    
    def cleanup_database_environment(self, conn, clean_file: str):
        """Clean up database environment using clean.sql file"""
        cursor = conn.cursor()
        
        try:
            if Path(clean_file).exists():
                with open(clean_file, 'r') as f:
                    clean_sql = f.read()
                    statements = clean_sql.split(';')
                    for stmt in statements:
                        stmt = stmt.strip()
                        if stmt:
                            try:
                                cursor.execute(stmt)
                                logging.debug(f"Executing cleanup SQL: {stmt[:50]}...")
                            except Exception as e:
                                logging.error(f"Cleanup SQL execution failed: {e}")
                conn.commit()
                logging.info("Database environment cleaned up successfully using clean.sql")
            else:
                logging.warning(f"Clean file not found: {clean_file}, skipping cleanup")
            
        except Exception as e:
            logging.error(f"Failed to cleanup database environment: {e}")
        finally:
            cursor.close()
    
    async def evaluate_with_llm(self, agent_response: str, expected_result: str, 
                               scoring_rules: str, sql_query: str) -> Dict[str, Any]:
        """Score using LLM"""
        if not agent_response:
            return {"score": 0, "explanation": "Agent did not provide a response"}
        
        # Use Jinja2 to render template
        template = self.template_env.get_template('evaluation.tpl')
        
        prompt = template.render(
            sql_query=sql_query,
            expected_result=expected_result,
            agent_optimization=agent_response,
            scoring_rules=scoring_rules
        )
        
        try:
            logging.debug("Calling LLM API for scoring...")
            headers = {
                'Authorization': f'Bearer {self.llm_config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.llm_config['model'],
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': self.llm_config['max_tokens'],
                'temperature': self.llm_config['temperature']
            }
            
            response = requests.post(
                f"{self.llm_config['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            llm_response = result['choices'][0]['message']['content']
            
            # Parse JSON response - try to extract JSON from response
            try:
                eval_outcome = json.loads(llm_response)
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it's wrapped in other text
                import re
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    eval_outcome = json.loads(json_match.group())
                else:
                    # Fallback: create a basic response
                    eval_outcome = {
                        "score": 0,
                        "explanation": f"Failed to parse LLM response: {llm_response[:100]}..."
                    }
            return eval_outcome
            
        except Exception as e:
            logging.error(f"LLM scoring failed: {e}")
            return {"score": 0, "explanation": f"Scoring failed: {str(e)}"}
    
    async def evaluate(self, agents: Union[SQLAgent, List[SQLAgent]], 
                      datasets: Optional[List[str]] = None,
                      auto_cleanup: bool = True) -> Dict[str, List[EvaluationResult]]:
        """Evaluate SQL Agent(s)
        
        This method can work in two modes:
        1. Auto mode (default): Automatically prepares environment, evaluates, and cleans up
        2. Manual mode: Uses pre-prepared environment via prepare_environment()
        
        Evaluation flow:
        1. For each dataset:
           - Setup database environment (schema.sql + data.sql) if not already prepared
           - For each agent: evaluate on this dataset
           - Cleanup database environment if auto_cleanup=True
        2. Next dataset
        
        Args:
            agents: Single SQLAgent or List of SQLAgent instances to evaluate
            datasets: List of dataset names to evaluate, if None then evaluate all datasets
            auto_cleanup: If True, automatically cleans up after each dataset. 
                         Set to False if you want to manually control cleanup.
            
        Returns:
            Dict mapping dataset names to lists of evaluation results for each agent
            
        Example:
            >>> # Auto mode (default)
            >>> evaluator.evaluate(agent)
            
            >>> # Manual mode
            >>> evaluator.prepare_environment()
            >>> evaluator.evaluate(agent, auto_cleanup=False)
            >>> evaluator.clean_environment()
            >>> evaluator.close_connection()
        """
        # Normalize agents to list - always treat as multiple agents
        if isinstance(agents, SQLAgent):
            agents_list = [agents]
        else:
            agents_list = agents
        
        print(f"🚀 Starting evaluation for {len(agents_list)} agent(s)")
        logging.info(f"Starting evaluation for {len(agents_list)} agent(s)")
        
        # Check if environment is already prepared
        use_prepared_env = (hasattr(self, '_active_connection') and 
                           self._active_connection is not None and
                           hasattr(self, '_active_datasets') and
                           self._active_datasets)
        
        if use_prepared_env:
            print("♻️  Using pre-prepared environment")
            available_datasets = self._active_datasets
            conn = self._active_connection
            # Filter datasets if specified
            if datasets:
                available_datasets = [d for d in available_datasets if d['name'] in datasets]
        else:
            # Auto mode: prepare environment
            available_datasets, conn = self._prepare_evaluation_environment(datasets)
            if not available_datasets or not conn:
                return {}
        
        # Results grouped by dataset
        dataset_results = {}
        
        # Process each dataset with proper cleanup
        for dataset_idx, dataset in enumerate(available_datasets, 1):
            dataset_name = dataset['name']
            print(f"\n📋 [{dataset_idx}/{len(available_datasets)}] Processing dataset: {dataset_name}")
            logging.info(f"Processing dataset: {dataset_name}")
            
            # Setup database environment (skip if using pre-prepared environment OR if tables already exist)
            if not use_prepared_env:
                # Check if dataset tables already exist in database
                tables_exist = self._check_dataset_tables_exist(conn, dataset_name)
                
                if tables_exist:
                    print(f"♻️  Dataset tables already exist, reusing existing environment")
                    logging.info(f"Reusing existing tables for dataset: {dataset_name}")
                else:
                    print(f"🗄️  Setting up database environment...")
                    self.setup_database_with_connection(conn, dataset['schema_file'], dataset['data_file'])
            
            # Parse questions once
            questions = self.parse_questions(dataset['questions_file'])
            print(f"📖 Dataset contains {len(questions)} questions")
            
            # Evaluate all agents
            dataset_results[dataset_name] = []
            for agent_idx, agent in enumerate(agents_list, 1):
                print(f"\n  🤖 [{agent_idx}/{len(agents_list)}] Evaluating Agent: {agent.get_name()}")
                logging.info(f"Evaluating Agent: {agent.get_name()} on dataset: {dataset_name}")
                
                agent_results = await self._evaluate_agent_on_dataset(
                    agent, questions, dataset_name
                )
                
                result = EvaluationResult(agent_results, agent.get_name(), self.dataset_weights)
                dataset_results[dataset_name].append(result)
                
                print(f"  ✅ Agent {agent.get_name()} completed on dataset {dataset_name}")
            
            # Cleanup database environment (if auto_cleanup is enabled and not using manual mode)
            if auto_cleanup and not use_prepared_env:
                print(f"🧹 Cleaning up database environment...")
                self.cleanup_database_environment(conn, dataset['clean_file'])
            
            print(f"🎉 Dataset {dataset_name} evaluation completed for all agents")
            logging.info(f"Dataset {dataset_name} evaluation completed for all agents")
        
        # Close connection only in auto mode
        if not use_prepared_env:
            conn.close()
            print(f"\n🏆 All evaluations completed!")
        else:
            print(f"\n🏆 All evaluations completed! (Connection kept open for manual management)")
        
        # Display evaluation summary table
        self._display_summary_table(dataset_results, agents_list)
        
        # Save detailed reports for each agent and dataset
        print("\n💾 Saving detailed reports...")
        for dataset_name, agent_results in dataset_results.items():
            for result in agent_results:
                agent_name = result.get_summary()['agent_name'].replace(' ', '_').lower()
                report_path = f"reports/{agent_name}_{dataset_name}_report.md"
                result.save_report(report_path)
        
        print("\n✅ Evaluation completed!")
        
        return dataset_results
    
    def _display_summary_table(self, dataset_results: Dict[str, List[EvaluationResult]], agents: List[SQLAgent]):
        """Display evaluation summary table with scores and weights"""
        print("\n" + "="*90)
        print("📊 Evaluation Summary Table")
        print("="*90)
        
        # Collect agent names
        agent_names = [agent.get_name() for agent in agents]
        
        # Create table header
        header = f"{'Dataset':<25} {'Weight':>6}"
        for agent_name in agent_names:
            header += f" | {agent_name:>15}"
        print(header)
        print("-" * len(header))
        
        # Calculate total scores for each agent
        agent_total_scores = {agent_name: 0.0 for agent_name in agent_names}
        
        # Create table rows for each dataset
        for dataset_name, agent_results in sorted(dataset_results.items()):
            # Get dataset weight
            weight = self.dataset_weights.get(dataset_name, 0)
            row = f"{dataset_name:<25} {weight:>5}%"
            
            for i, result in enumerate(agent_results):
                # Calculate dataset-specific score (actual score out of max)
                total_score = sum(q['score'] for q in result.results)
                max_score = len(result.results) * 10
                row += f" | {total_score:>6.0f}/{max_score:<6}"
                
                # Calculate weighted contribution for total
                dataset_score_pct = (total_score / max_score) if max_score > 0 else 0
                weighted_contribution = dataset_score_pct * weight
                agent_total_scores[agent_names[i]] += weighted_contribution
            
            print(row)
        
        # Print separator
        print("-" * len(header))
        
        # Print total row
        total_row = f"{'TOTAL':<25} {'100':>5}%"
        for agent_name in agent_names:
            total_score = agent_total_scores[agent_name]
            total_row += f" | {total_score:>6.1f}/100   "
        print(total_row)
        
        print("="*90)
