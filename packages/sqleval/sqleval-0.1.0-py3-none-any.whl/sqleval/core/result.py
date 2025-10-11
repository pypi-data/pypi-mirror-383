"""Evaluation result processing class"""

from typing import List, Dict, Any
from datetime import datetime
import json


class EvaluationResult:
    """Evaluation result class"""
    
    def __init__(self, results: List[Dict[str, Any]], agent_name: str = "Unknown", dataset_weights: Dict[str, int] = None):
        self.results = results
        self.agent_name = agent_name
        self.timestamp = datetime.now()
        self.dataset_weights = dataset_weights or {}
        
    def get_total_score(self) -> float:
        """Get total weighted score (out of 100)"""
        if not self.dataset_weights:
            # Fallback to simple sum if no weights configured
            return sum(r['score'] for r in self.results)
        
        # Group results by dataset
        dataset_scores = {}
        for result in self.results:
            dataset = result['dataset']
            if dataset not in dataset_scores:
                dataset_scores[dataset] = []
            dataset_scores[dataset].append(result['score'])
        
        # Calculate weighted score
        weighted_score = 0.0
        total_weight = sum(self.dataset_weights.values())
        
        for dataset, scores in dataset_scores.items():
            weight = self.dataset_weights.get(dataset, 0)
            if weight > 0 and total_weight > 0:
                # Calculate average score for this dataset
                avg_score = sum(scores) / len(scores)
                # Weighted contribution: (avg_score/10) * (weight/total_weight) * 100
                weighted_score += (avg_score / 10.0) * (weight / total_weight) * 100
        
        return weighted_score
    
    def get_max_score(self) -> float:
        """Get maximum possible score (100)"""
        return 100.0
    
    def get_average_score(self) -> float:
        """Get average score per question (out of 10)"""
        if not self.results:
            return 0.0
        return sum(r['score'] for r in self.results) / len(self.results)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get evaluation summary"""
        return {
            'agent_name': self.agent_name,
            'timestamp': self.timestamp.isoformat(),
            'total_questions': len(self.results),
            'total_score': self.get_total_score(),
            'max_score': self.get_max_score(),
            'score_percentage': (self.get_total_score() / self.get_max_score() * 100) if self.get_max_score() > 0 else 0
        }
    
    def print_summary(self):
        """Print evaluation summary to console"""
        summary = self.get_summary()
        print(f"\n🏆 SQL Agent Evaluation Results")
        print(f"Agent: {summary['agent_name']}")
        print(f"Evaluation Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Questions: {summary['total_questions']}")
        print(f"Score: {summary['total_score']:.1f}/100")
    
    def save_report(self, filepath: str = None):
        """Save detailed report to file"""
        if filepath is None:
            filepath = f"reports/{self.agent_name}_evaluation_report.md"
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        summary = self.get_summary()
        
        report_content = f"""# SQL Agent Evaluation Detailed Report

**Agent Name**: {summary['agent_name']}  
**Evaluation Time**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Questions Evaluated**: {summary['total_questions']}  
**Score**: {summary['total_score']:.1f}/100

**Dataset Weights**: {self.dataset_weights if self.dataset_weights else 'No weights configured'}

---

"""
        
        # Group by dataset
        datasets = {}
        for result in self.results:
            dataset = result['dataset']
            if dataset not in datasets:
                datasets[dataset] = []
            datasets[dataset].append(result)
        
        for dataset_name, dataset_results in datasets.items():
            dataset_score = sum(r['score'] for r in dataset_results)
            dataset_avg = dataset_score / len(dataset_results)
            weight = self.dataset_weights.get(dataset_name, 0)
            
            # Calculate weighted score using the same logic as get_total_score
            total_weight = sum(self.dataset_weights.values())
            if weight > 0 and total_weight > 0:
                weighted_score = (dataset_avg / 10.0) * (weight / total_weight) * 100
            else:
                weighted_score = 0.0
            
            report_content += f"""## Dataset: {dataset_name}

**Score**: {dataset_score:.1f}/{len(dataset_results) * 10} (Average: {dataset_avg:.1f}/10)  
**Weight**: {weight}  
**Weighted Score**: {weighted_score:.1f}/100  
**Question Count**: {len(dataset_results)}

### Quick Score Summary
"""
            
            # Add quick score summary for each question
            for i, result in enumerate(dataset_results, 1):
                report_content += f"- **Q{i}**: {result['score']}/10 - {result['title']}\n"
            
            report_content += "\n### Detailed Analysis\n\n"
            
            for i, result in enumerate(dataset_results, 1):
                # Use markdown code block with indentation to prevent conflicts
                agent_response_lines = result['agent_optimization'].split('\n')
                indented_response = '\n'.join(f"    {line}" for line in agent_response_lines)
                
                report_content += f"""### Question {i}: {result['title']}

**Score**: {result['score']}/10

**Scoring Explanation**: {result['explanation']}

**SQL Query**:
```sql
{result['sql']}
```

**Expected Result**: {result['expected']}

**Agent Response**:
```markdown
{indented_response}
```

---

"""
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📝 Detailed report saved to {filepath}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'summary': self.get_summary(),
            'results': self.results
        }
    
    def save_json(self, filepath: str):
        """Save as JSON format"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"📄 JSON report saved to {filepath}")
