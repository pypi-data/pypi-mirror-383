import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, date
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class PostgresClient:
    def __init__(self):
        self.POSTGRES_URI = os.getenv("POSTGRES_URI")
        if not self.POSTGRES_URI:
            raise ValueError("POSTGRES_URI environment variable not set")
    
    def _serialize_datetime(self, obj):
        """Convert datetime objects to ISO format strings"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return obj
    
    def _process_results(self, results):
        """Process query results to handle datetime serialization"""
        if not results:
            return results
        
        processed_results = []
        for row in results:
            processed_row = {}
            for key, value in dict(row).items():
                processed_row[key] = self._serialize_datetime(value)
            processed_results.append(processed_row)
        return processed_results
    
    def get_connection(self):
        """Get a new database connection."""
        return psycopg2.connect(self.POSTGRES_URI)
    
    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results.
        
        Args:
            sql_query: The SQL query to execute
            
        Returns:
            Dictionary containing query results or error message
        """
        conn = None
        cursor = None
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            logger.info(f"Executing SQL query: {sql_query}")
            cursor.execute(sql_query)
            
            # Handle SELECT queries and INSERT...RETURNING queries
            if (sql_query.strip().upper().startswith('SELECT') or 
                'RETURNING' in sql_query.upper()):
                results = cursor.fetchall()
                processed_results = self._process_results(results)
                logger.info(f"Query returned {len(results)} rows")
                # Commit for INSERT...RETURNING queries
                if not sql_query.strip().upper().startswith('SELECT'):
                    conn.commit()
                return {
                    "success": True, 
                    "data": processed_results, 
                    "row_count": len(results)
                }
            else:
                # For other non-SELECT queries, commit the transaction
                conn.commit()
                affected_rows = cursor.rowcount
                logger.info(f"Query affected {affected_rows} rows")
                return {
                    "success": True, 
                    "affected_rows": affected_rows
                }
                
        except psycopg2.Error as e:
            logger.error(f"Database error: {str(e)}")
            return {"success": False, "error": f"Database error: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Create singleton instance
postgres_client = PostgresClient()