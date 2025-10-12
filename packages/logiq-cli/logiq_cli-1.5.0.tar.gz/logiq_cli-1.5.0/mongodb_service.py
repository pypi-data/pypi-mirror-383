"""
MongoDB Service for CLI Tool

This module provides MongoDB connectivity using the same configuration as the server.
It reads from the same .env file and uses the same database structure.
"""

import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from dotenv import load_dotenv

# Load environment variables from server directory
server_dir = Path(__file__).parent.parent / "server"
env_file = server_dir / ".env"

if env_file.exists():
    load_dotenv(env_file)
else:
    # Try loading from current directory
    load_dotenv()

class MongoDBService:
    """MongoDB service for CLI tool using same config as server."""
    
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_URL')
        if not self.mongo_url:
            raise ValueError("MONGO_URL not found in environment variables")
        
        # Initialize both sync and async clients
        self.client = None
        self.async_client = None
        self.database = None
        self.async_database = None
        
        # Collection references
        self.user_collection = None
        self.analysis_collection = None
        self.monitoring_collection = None
        
    def connect(self):
        """Initialize synchronous MongoDB connection."""
        try:
            self.client = MongoClient(self.mongo_url)
            self.database = self.client.Forensiq
            
            # Initialize collections
            self.user_collection = self.database.get_collection("users")
            self.analysis_collection = self.database.get_collection("log_analysis")
            self.monitoring_collection = self.database.get_collection("monitoring_sessions")
            
            # Test connection
            self.client.admin.command('ping')
            return True
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def connect_async(self):
        """Initialize asynchronous MongoDB connection."""
        try:
            self.async_client = AsyncIOMotorClient(self.mongo_url)
            self.async_database = self.async_client.Forensiq
            
            # Test connection
            await self.async_client.admin.command('ping')
            return True
            
        except Exception as e:
            print(f"Failed to connect to MongoDB (async): {e}")
            return False
    
    def close(self):
        """Close MongoDB connections."""
        if self.client:
            self.client.close()
        if self.async_client:
            self.async_client.close()
    
    async def store_analysis_result(self, analysis_data: Dict[str, Any], username: str = None) -> Optional[str]:
        """
        Store analysis result in MongoDB.
        
        Args:
            analysis_data: Analysis result data
            username: Username of the authenticated user
            
        Returns:
            str: Inserted document ID or None if failed
        """
        try:
            if not self.async_client:
                await self.connect_async()
            
            # Use the provided username if available, otherwise fallback to the one in analysis_data
            user = username if username else analysis_data.get('user', 'unknown')
            
            # Prepare document
            document = {
                'timestamp': datetime.utcnow(),
                'user': user,
                'log_source': analysis_data.get('log_source', 'dynamic'),
                'analysis_result': analysis_data.get('result', {}),
                'processing_time_ms': analysis_data.get('processing_time_ms', 0),
                'ai_agent_analysis': analysis_data.get('ai_agent_analysis', {}),
                'log_content_hash': analysis_data.get('log_content_hash', ''),
                'status': 'completed'
            }
            
            collection = self.async_database.get_collection("analysis_results")
            result = await collection.insert_one(document)
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Failed to store analysis result: {e}")
            return None
    
    async def store_monitoring_session(self, session_data: Dict[str, Any]) -> Optional[str]:
        """
        Store monitoring session in MongoDB.
        
        Args:
            session_data: Monitoring session data
            
        Returns:
            str: Inserted document ID or None if failed
        """
        try:
            if not self.async_client:
                await self.connect_async()
            
            # Prepare document
            document = {
                'timestamp': datetime.utcnow(),
                'user': session_data.get('user', 'unknown'),
                'log_sources': session_data.get('log_sources', []),
                'interval_seconds': session_data.get('interval_seconds', 300),
                'status': session_data.get('status', 'active'),
                'session_id': session_data.get('session_id', ''),
                'total_analyses': session_data.get('total_analyses', 0),
                'last_analysis': session_data.get('last_analysis'),
                'ai_agent_enabled': session_data.get('ai_agent_enabled', False)
            }
            
            collection = self.async_database.get_collection("monitoring_sessions")
            result = await collection.insert_one(document)
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Failed to store monitoring session: {e}")
            return None
    
    async def get_analysis_results(self, limit: int = 10, user: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve analysis results from MongoDB.
        
        Args:
            limit: Maximum number of results to return
            user: Filter by user (optional)
            
        Returns:
            List of analysis results
        """
        try:
            if not self.async_client:
                await self.connect_async()
            
            collection = self.async_database.get_collection("log_analysis")
            
            # Build query
            query = {}
            if user:
                query['user'] = user
            
            # Get results
            cursor = collection.find(query).sort('timestamp', -1).limit(limit)
            results = []
            
            async for document in cursor:
                # Convert ObjectId to string for JSON serialization
                document['_id'] = str(document['_id'])
                if 'timestamp' in document:
                    document['timestamp'] = document['timestamp'].isoformat()
                results.append(document)
            
            return results
            
        except Exception as e:
            print(f"Failed to retrieve analysis results: {e}")
            return []
    
    async def get_monitoring_sessions(self, limit: int = 10, user: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve monitoring sessions from MongoDB.
        
        Args:
            limit: Maximum number of sessions to return
            user: Filter by user (optional)
            
        Returns:
            List of monitoring sessions
        """
        try:
            if not self.async_client:
                await self.connect_async()
            
            collection = self.async_database.get_collection("monitoring_sessions")
            
            # Build query
            query = {}
            if user:
                query['user'] = user
            
            # Get results
            cursor = collection.find(query).sort('timestamp', -1).limit(limit)
            results = []
            
            async for document in cursor:
                # Convert ObjectId to string for JSON serialization
                document['_id'] = str(document['_id'])
                if 'timestamp' in document:
                    document['timestamp'] = document['timestamp'].isoformat()
                if 'last_analysis' in document and document['last_analysis']:
                    document['last_analysis'] = document['last_analysis'].isoformat()
                results.append(document)
            
            return results
            
        except Exception as e:
            print(f"Failed to retrieve monitoring sessions: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about MongoDB collections.
        
        Returns:
            Dict containing collection statistics
        """
        try:
            if not self.async_client:
                await self.connect_async()
            
            stats = {}
            
            # Get collection counts
            analysis_count = await self.async_database.get_collection("log_analysis").count_documents({})
            monitoring_count = await self.async_database.get_collection("monitoring_sessions").count_documents({})
            user_count = await self.async_database.get_collection("users").count_documents({})
            
            stats = {
                'database_name': 'Forensiq',
                'collections': {
                    'log_analysis': {
                        'count': analysis_count,
                        'description': 'Log analysis results'
                    },
                    'monitoring_sessions': {
                        'count': monitoring_count,
                        'description': 'Monitoring session records'
                    },
                    'users': {
                        'count': user_count,
                        'description': 'User accounts'
                    }
                },
                'total_documents': analysis_count + monitoring_count + user_count,
                'connection_status': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            print(f"Failed to get collection stats: {e}")
            return {'error': str(e), 'connection_status': 'failed'}
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get MongoDB connection information."""
        return {
            'mongo_url': self.mongo_url.replace(self.mongo_url.split('@')[0].split('//')[1], '****') if '@' in self.mongo_url else self.mongo_url,
            'database': 'Forensiq',
            'connected': self.client is not None or self.async_client is not None
        }

    async def create_monitoring_session(self, username: str, log_sources: List[str], interval: int) -> Optional[str]:
        """Create a new monitoring session and return session ID."""
        session_data = {
            'user': username,
            'log_sources': log_sources,
            'interval_seconds': interval,
            'status': 'active',
            'session_id': f"session_{int(datetime.utcnow().timestamp())}",
            'total_analyses': 0,
            'ai_agent_enabled': True
        }
        return await self.store_monitoring_session(session_data)
    
    async def update_monitoring_session(self, session_id: str, **updates) -> bool:
        """Update monitoring session with new data."""
        try:
            if not self.async_client:
                await self.connect_async()
            
            collection = self.async_database.get_collection("monitoring_sessions")
            
            # Update document
            update_data = {'$set': updates}
            result = await collection.update_one(
                {'session_id': session_id},
                update_data
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Failed to update monitoring session: {e}")
            return False

    async def store_analysis_result_with_session(self, analysis_data: Dict[str, Any], username: str, session_id: str) -> Optional[str]:
        """Store analysis result with session information."""
        enhanced_data = {
            **analysis_data,
            'user': username,
            'session_id': session_id
        }
        return await self.store_analysis_result(enhanced_data)

# Global instance
mongodb_service = MongoDBService()

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import json
import hashlib

class MongoDBService:
    """Service for handling MongoDB operations with your existing database."""
    
    def __init__(self, mongo_url: str = "mongodb://localhost:27017"):
        """
        Initialize MongoDB service with your server's configuration.
        
        Args:
            mongo_url: MongoDB connection URL (should match your server config)
        """
        self.mongo_url = mongo_url
        self.client = None
        self.database = None
        self.logger = logging.getLogger("ForensIQ.MongoDB")
        
        # Collection references (matching your server setup)
        self.user_collection = None
        self.analysis_collection = None
        self.monitoring_collection = None
    
    async def connect(self) -> bool:
        """Connect to MongoDB database."""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.database = self.client.Forensiq  # Same as your server
            
            # Get collection references
            self.user_collection = self.database.get_collection("users")
            self.analysis_collection = self.database.get_collection("log_analysis")
            self.monitoring_collection = self.database.get_collection("monitoring_sessions")
            
            # Test connection
            await self.client.admin.command('ping')
            self.logger.info(f"Connected to MongoDB at {self.mongo_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            self.logger.info("Disconnected from MongoDB")
    
    async def store_analysis_result(self, analysis_data: Dict[str, Any], 
                                  username: str, session_id: Optional[str] = None) -> str:
        """
        Store analysis result in MongoDB in real-time.
        
        Args:
            analysis_data: The analysis result from ForensIQ API
            username: Username of the person who ran the analysis
            session_id: Optional monitoring session ID
            
        Returns:
            str: Analysis ID of the stored result
        """
        try:
            # Generate unique analysis ID
            analysis_id = hashlib.sha256(
                f"{username}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            
            # Create log content hash if log content is available
            log_content = analysis_data.get('original_log_content', '')
            log_content_hash = hashlib.sha256(log_content.encode()).hexdigest()
            
            # Prepare the document for MongoDB
            stored_analysis = {
                "analysis_id": analysis_id,
                "session_id": session_id,
                "username": username,
                "log_content_hash": log_content_hash,
                "log_file_path": analysis_data.get('log_file_path'),
                
                # Analysis request details
                "request_timestamp": datetime.utcnow(),
                "enhance_with_ai": analysis_data.get('enhance_with_ai', True),
                "max_results": analysis_data.get('max_results', 5),
                
                # Analysis results
                "summary": analysis_data.get('summary', ''),
                "matched_techniques": analysis_data.get('matched_techniques', []),
                "enhanced_analysis": analysis_data.get('enhanced_analysis'),
                "processing_time_ms": analysis_data.get('processing_time_ms'),
                
                # AI Agent data (if available)
                "ai_agent_analysis": analysis_data.get('ai_agent_analysis'),
                "detected_patterns": analysis_data.get('detected_patterns'),
                "threat_context": analysis_data.get('threat_context'),
                
                # Metadata
                "created_at": datetime.utcnow(),
                "file_size": len(log_content) if log_content else None,
                "analysis_source": "cli_tool"
            }
            
            # Insert into MongoDB
            result = await self.analysis_collection.insert_one(stored_analysis)
            self.logger.info(f"Stored analysis result with ID: {analysis_id}")
            
            return analysis_id
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis result: {e}")
            raise
    
    async def create_monitoring_session(self, username: str, log_sources: List[str], 
                                      interval: int = 300) -> str:
        """
        Create a new monitoring session in MongoDB.
        
        Args:
            username: Username starting the session
            log_sources: List of log sources to monitor
            interval: Monitoring interval in seconds
            
        Returns:
            str: Session ID
        """
        try:
            session_id = hashlib.sha256(
                f"{username}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:12]
            
            session_data = {
                "session_id": session_id,
                "username": username,
                "log_sources": log_sources,
                "start_time": datetime.utcnow(),
                "end_time": None,
                "status": "active",
                "interval_seconds": interval,
                "total_analyses": 0,
                "last_analysis": None,
                "ai_agent_enabled": True
            }
            
            await self.monitoring_collection.insert_one(session_data)
            self.logger.info(f"Created monitoring session: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create monitoring session: {e}")
            raise
    
    async def update_monitoring_session(self, session_id: str, **updates):
        """Update monitoring session with new data."""
        try:
            await self.monitoring_collection.update_one(
                {"session_id": session_id},
                {"$set": updates}
            )
            self.logger.debug(f"Updated monitoring session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update monitoring session: {e}")
    
    async def get_analysis_results(self, username: str = None, limit: int = 50, 
                                 skip: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve analysis results from MongoDB.
        
        Args:
            username: Filter by username (optional)
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of analysis results
        """
        try:
            query = {}
            if username:
                query["username"] = username
            
            cursor = self.analysis_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            results = []
            
            async for document in cursor:
                # Convert ObjectId to string for JSON serialization
                document["_id"] = str(document["_id"])
                results.append(document)
            
            self.logger.info(f"Retrieved {len(results)} analysis results")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve analysis results: {e}")
            return []
    
    async def get_monitoring_sessions(self, username: str = None, 
                                    active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve monitoring sessions from MongoDB.
        
        Args:
            username: Filter by username (optional)
            active_only: Only return active sessions
            
        Returns:
            List of monitoring sessions
        """
        try:
            query = {}
            if username:
                query["username"] = username
            if active_only:
                query["status"] = "active"
            
            cursor = self.monitoring_collection.find(query).sort("start_time", -1)
            sessions = []
            
            async for document in cursor:
                document["_id"] = str(document["_id"])
                sessions.append(document)
            
            self.logger.info(f"Retrieved {len(sessions)} monitoring sessions")
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve monitoring sessions: {e}")
            return []
    
    async def get_analysis_stats(self, username: str = None) -> Dict[str, Any]:
        """
        Get analysis statistics from MongoDB.
        
        Args:
            username: Filter by username (optional)
            
        Returns:
            Dictionary with analysis statistics
        """
        try:
            query = {}
            if username:
                query["username"] = username
            
            # Total analyses
            total_analyses = await self.analysis_collection.count_documents(query)
            
            # Analyses today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_query = query.copy()
            today_query["created_at"] = {"$gte": today_start}
            analyses_today = await self.analysis_collection.count_documents(today_query)
            
            # Recent techniques
            recent_pipeline = [
                {"$match": query},
                {"$sort": {"created_at": -1}},
                {"$limit": 100},
                {"$unwind": "$matched_techniques"},
                {"$group": {
                    "_id": "$matched_techniques.technique_id",
                    "count": {"$sum": 1},
                    "name": {"$first": "$matched_techniques.name"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            top_techniques = []
            async for doc in self.analysis_collection.aggregate(recent_pipeline):
                top_techniques.append(doc)
            
            return {
                "total_analyses": total_analyses,
                "analyses_today": analyses_today,
                "top_techniques": top_techniques,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis stats: {e}")
            return {
                "total_analyses": 0,
                "analyses_today": 0,
                "top_techniques": [],
                "error": str(e)
            }
    
    async def search_analyses(self, search_term: str, username: str = None) -> List[Dict[str, Any]]:
        """
        Search analysis results by content.
        
        Args:
            search_term: Term to search for
            username: Filter by username (optional)
            
        Returns:
            List of matching analysis results
        """
        try:
            query = {
                "$or": [
                    {"summary": {"$regex": search_term, "$options": "i"}},
                    {"enhanced_analysis": {"$regex": search_term, "$options": "i"}},
                    {"matched_techniques.name": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            if username:
                query["username"] = username
            
            cursor = self.analysis_collection.find(query).sort("created_at", -1).limit(20)
            results = []
            
            async for document in cursor:
                document["_id"] = str(document["_id"])
                results.append(document)
            
            self.logger.info(f"Found {len(results)} analyses matching '{search_term}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search analyses: {e}")
            return []
