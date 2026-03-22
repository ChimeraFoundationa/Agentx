"""
ERC-8004 Validation Registry Implementation

Record and verify task completion proofs:
- Record validation results
- Query validation history
- Support for various validation strategies
"""

import json
from typing import List, Dict, Optional, Any
from web3 import Web3
from web3.contract import Contract
from datetime import datetime


class ValidationRecorder:
    """
    Record and manage validation results for AI agent tasks
    """
    
    # Default Validation Registry addresses (update after deployment)
    REGISTRY_ADDRESSES = {
        "ethereum": "0x...",
        "base": "0x...",
        "base_sepolia": "0x...",
        "sepolia": "0x...",
        "anvil": "0x948B3c65b89DF0B4894ABE91E6D02FE579834F8F",  # Local testnet
    }
    
    # ABI for Validation Registry (simplified)
    VALIDATION_REGISTRY_ABI = [
        {
            "inputs": [
                {"name": "agentId", "type": "uint256"},
                {"name": "taskId", "type": "bytes32"},
                {"name": "success", "type": "bool"},
                {"name": "evidence", "type": "bytes"}
            ],
            "name": "recordValidation",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "agentId", "type": "uint256"}],
            "name": "getValidationRecords",
            "outputs": [
                {
                    "components": [
                        {"name": "taskId", "type": "bytes32"},
                        {"name": "success", "type": "bool"},
                        {"name": "evidence", "type": "bytes"},
                        {"name": "validator", "type": "address"},
                        {"name": "timestamp", "type": "uint256"}
                    ],
                    "name": "records",
                    "type": "tuple[]"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"name": "agentId", "type": "uint256"},
                {"name": "taskId", "type": "bytes32"}
            ],
            "name": "getValidationRecord",
            "outputs": [
                {
                    "components": [
                        {"name": "taskId", "type": "bytes32"},
                        {"name": "success", "type": "bool"},
                        {"name": "evidence", "type": "bytes"},
                        {"name": "validator", "type": "address"},
                        {"name": "timestamp", "type": "uint256"}
                    ],
                    "name": "record",
                    "type": "tuple"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "agentId", "type": "uint256"},
                {"indexed": True, "name": "taskId", "type": "bytes32"},
                {"indexed": False, "name": "success", "type": "bool"}
            ],
            "name": "ValidationRecorded",
            "type": "event"
        }
    ]
    
    def __init__(self, rpc_url: str, private_key: Optional[str] = None):
        """
        Initialize Validation Recorder
        
        Args:
            rpc_url: Ethereum RPC endpoint
            private_key: Optional private key for signing transactions
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
        
        self.contract = None
        self.chain_id = self.w3.eth.chain_id
    
    def set_registry_address(self, address: str):
        """Set the Validation Registry contract address"""
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=self.VALIDATION_REGISTRY_ABI
        )
    
    def generate_task_id(self, task_description: str) -> bytes:
        """
        Generate unique task ID from description
        
        Args:
            task_description: Description of the task
        
        Returns:
            bytes32 task ID
        """
        return Web3.keccak(text=task_description)
    
    def encode_evidence(self, evidence_data: Dict[str, Any]) -> bytes:
        """
        Encode evidence data to bytes
        
        Args:
            evidence_data: Evidence dictionary
        
        Returns:
            Encoded evidence bytes
        """
        return json.dumps(evidence_data).encode('utf-8')
    
    def record_validation(
        self,
        agent_token_id: int,
        task_id: bytes,
        success: bool,
        evidence_data: Dict[str, Any]
    ) -> str:
        """
        Record validation result for a task
        
        Args:
            agent_token_id: Agent's token ID
            task_id: Task identifier (bytes32)
            success: Whether task was completed successfully
            evidence_data: Evidence of completion/failure
        
        Returns:
            Transaction hash
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        if not self.account:
            raise ValueError("Private key required to record validation.")
        
        # Encode evidence
        evidence_bytes = self.encode_evidence(evidence_data)
        
        # Build transaction
        tx = self.contract.functions.recordValidation(
            agent_token_id,
            task_id,
            success,
            evidence_bytes
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "chainId": self.chain_id,
            "gas": 150000,
            "gasPrice": self.w3.eth.gas_price
        })
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return tx_hash.hex()
    
    def record_task_completion(
        self,
        agent_token_id: int,
        task_name: str,
        task_result: Dict[str, Any],
        success: bool
    ) -> str:
        """
        Convenience method to record task completion
        
        Args:
            agent_token_id: Agent's token ID
            task_name: Name of the task
            task_result: Task result details
            success: Whether task succeeded
        
        Returns:
            Transaction hash
        """
        task_id = self.generate_task_id(f"{task_name}:{datetime.utcnow().isoformat()}")
        
        evidence = {
            "task_name": task_name,
            "timestamp": datetime.utcnow().isoformat(),
            "result": task_result,
            "validator": self.address
        }
        
        return self.record_validation(agent_token_id, task_id, success, evidence)
    
    def get_validation_records(self, agent_token_id: int) -> List[Dict[str, Any]]:
        """
        Get all validation records for an agent
        
        Args:
            agent_token_id: Agent's token ID
        
        Returns:
            List of validation records
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        records = self.contract.functions.getValidationRecords(agent_token_id).call()
        
        return [
            {
                "task_id": rec[0].hex(),
                "success": rec[1],
                "evidence": self._decode_evidence(rec[2]),
                "validator": rec[3],
                "timestamp": datetime.fromtimestamp(rec[4])
            }
            for rec in records
        ]
    
    def _decode_evidence(self, evidence_bytes: bytes) -> Dict[str, Any]:
        """Decode evidence bytes to dictionary"""
        try:
            return json.loads(evidence_bytes.decode('utf-8'))
        except:
            return {"raw": evidence_bytes.hex()}
    
    def get_validation_record(
        self,
        agent_token_id: int,
        task_id: bytes
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific validation record by task ID
        
        Args:
            agent_token_id: Agent's token ID
            task_id: Task identifier
        
        Returns:
            Validation record or None if not found
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        try:
            record = self.contract.functions.getValidationRecord(
                agent_token_id,
                task_id
            ).call()
            
            return {
                "task_id": record[0].hex(),
                "success": record[1],
                "evidence": self._decode_evidence(record[2]),
                "validator": record[3],
                "timestamp": datetime.fromtimestamp(record[4])
            }
        except:
            return None
    
    def get_success_rate(self, agent_token_id: int, limit: int = 100) -> float:
        """
        Calculate success rate for an agent
        
        Args:
            agent_token_id: Agent's token ID
            limit: Number of recent records to consider
        
        Returns:
            Success rate (0.0 - 1.0)
        """
        records = self.get_validation_records(agent_token_id)
        
        if not records:
            return 0.0
        
        recent = records[-limit:] if len(records) >= limit else records
        successes = sum(1 for rec in recent if rec["success"])
        
        return successes / len(recent)
    
    def get_validation_summary(self, agent_token_id: int) -> Dict[str, Any]:
        """
        Get comprehensive validation summary for an agent
        
        Args:
            agent_token_id: Agent's token ID
        
        Returns:
            Validation summary dictionary
        """
        records = self.get_validation_records(agent_token_id)
        
        total = len(records)
        successes = sum(1 for rec in records if rec["success"])
        failures = total - successes
        
        success_rate = successes / total if total > 0 else 0.0
        
        # Task type breakdown
        task_types = {}
        for rec in records:
            task_name = rec["evidence"].get("task_name", "unknown")
            if task_name not in task_types:
                task_types[task_name] = {"total": 0, "successes": 0}
            task_types[task_name]["total"] += 1
            if rec["success"]:
                task_types[task_name]["successes"] += 1
        
        return {
            "token_id": agent_token_id,
            "total_validations": total,
            "successes": successes,
            "failures": failures,
            "success_rate": round(success_rate, 4),
            "task_breakdown": task_types,
            "last_validation": records[-1]["timestamp"] if records else None
        }
