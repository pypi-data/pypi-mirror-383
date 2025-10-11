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
            env_file: .env file path, if None then try to load config/.env
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load default .env file
            env_paths = [
                "config/.env",
                ".env",
                "../config/.env"
            ]
            for env_path in env_paths:
                if Path(env_path).exists():
                    load_dotenv(env_path)
                    logging.info(f"Environment variables loaded from: {env_path}")
                    break
        
        self.datasets_path = Path(datasets_path)
        self.prompts_path = Path(prompts_path)
        
        # Database configuration
        self.db_config = database_config or {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', 3306)),
            'user': os.getenv('DATABASE_USER', 'root'),
            'password': os.getenv('DATABASE_PASSWORD', ''),
            'database': os.getenv('DATABASE_NAME', 'sql_eval_test')
        }
        
        # LLM configuration
        self.llm_config = llm_config or {
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
    
    def _prepare_evaluation_environment(self, datasets: Optional[List[str]] = None) -> tuple:
        """Prepare evaluation environment - common logic for both evaluation methods
        
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
        
        # Execute data
        with open(data_file, 'r') as f:
            data_sql = f.read()
            statements = data_sql.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt.upper().startswith('INSERT'):
                    try:
                        cursor.execute(stmt)
                        logging.debug(f"Inserting data: {stmt[:30]}...")
                    except Exception as e:
                        if "Duplicate entry" in str(e):
                            logging.debug("Data already exists, skipping")
                        else:
                            logging.error(f"Data insertion failed: {e}")
        
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
                      datasets: Optional[List[str]] = None) -> Dict[str, List[EvaluationResult]]:
        """Evaluate SQL Agent(s)
        
        Correct flow:
        1. For each dataset:
           - Setup database environment (schema.sql + data.sql)
           - For each agent: evaluate on this dataset
           - Cleanup database environment (drop all tables)
        2. Next dataset
        
        Args:
            agents: Single SQLAgent or List of SQLAgent instances to evaluate
            datasets: List of dataset names to evaluate, if None then evaluate all datasets
            
        Returns:
            Dict mapping dataset names to lists of evaluation results for each agent
        """
        # Normalize agents to list - always treat as multiple agents
        if isinstance(agents, SQLAgent):
            agents_list = [agents]
        else:
            agents_list = agents
        
        print(f"🚀 Starting evaluation for {len(agents_list)} agent(s)")
        logging.info(f"Starting evaluation for {len(agents_list)} agent(s)")
        
        # Prepare evaluation environment
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
            
            # Setup database environment
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
            
            # Cleanup database environment
            print(f"🧹 Cleaning up database environment...")
            self.cleanup_database_environment(conn, dataset['clean_file'])
            
            print(f"🎉 Dataset {dataset_name} evaluation completed for all agents")
            logging.info(f"Dataset {dataset_name} evaluation completed for all agents")
        
        conn.close()
        print(f"\n🏆 All evaluations completed!")
        
        # Always display agent comparison (unified handling for single and multiple agents)
        print("\n" + "="*60)
        print("📊 Agent Accuracy Comparison")
        print("="*60)
        
        # Group results by agent and calculate combined scores
        agent_summaries = {}
        for dataset_name, agent_results in dataset_results.items():
            for result in agent_results:
                agent_name = result.get_summary()['agent_name']
                if agent_name not in agent_summaries:
                    agent_summaries[agent_name] = []
                agent_summaries[agent_name].append(result)
        
        # Display combined scores
        for agent_name, results in agent_summaries.items():
            # Combine all results from all datasets
            combined_results = []
            for result in results:
                combined_results.extend(result.results)
            
            # Create combined evaluation result
            combined_result = EvaluationResult(combined_results, agent_name, self.dataset_weights)
            summary = combined_result.get_summary()
            print(f"{summary['agent_name']:<20} {summary['total_score']:>6.1f}/100")
            
            # Save combined report
            combined_result.save_report(f"reports/{agent_name.replace(' ', '_').lower()}_combined_report.md")
        
        print("\n✅ Evaluation completed!")
        print("📄 Combined reports saved to reports/ directory")
        
        return dataset_results
