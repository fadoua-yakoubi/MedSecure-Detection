// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AttackLogger {
    struct AttackEvent {
        uint256 id;
        string timestamp;
        string email;
        string userId;
        string ipAddress;
        string country;
        string attackType;
        uint256 confidence;
        uint256 bertProbability;
        bool bertUsed;
        bool loginSuccessful;
        uint256 blockNumber;
        address logger;
    }
    
    AttackEvent[] public attacks;
    uint256 public attackCount;
    
    event AttackLogged(
        uint256 indexed id,
        string timestamp,
        string email,
        string attackType,
        uint256 confidence
    );
    
    function logAttack(
        string memory _timestamp,
        string memory _email,
        string memory _userId,
        string memory _ipAddress,
        string memory _country,
        string memory _attackType,
        uint256 _confidence,
        uint256 _bertProbability,
        bool _bertUsed,
        bool _loginSuccessful
    ) public {
        attackCount++;
        
        attacks.push(AttackEvent({
            id: attackCount,
            timestamp: _timestamp,
            email: _email,
            userId: _userId,
            ipAddress: _ipAddress,
            country: _country,
            attackType: _attackType,
            confidence: _confidence,
            bertProbability: _bertProbability,
            bertUsed: _bertUsed,
            loginSuccessful: _loginSuccessful,
            blockNumber: block.number,
            logger: msg.sender
        }));
        
        emit AttackLogged(
            attackCount,
            _timestamp,
            _email,
            _attackType,
            _confidence
        );
    }
    
    function getAttackCount() public view returns (uint256) {
        return attackCount;
    }
    
    function getAttack(uint256 _id) public view returns (
        uint256 id,
        string memory timestamp,
        string memory email,
        string memory userId,
        string memory ipAddress,
        string memory country,
        string memory attackType,
        uint256 confidence,
        uint256 bertProbability,
        bool bertUsed,
        bool loginSuccessful,
        uint256 blockNumber,
        address logger
    ) {
        require(_id > 0 && _id <= attackCount, "Invalid attack ID");
        AttackEvent memory attack = attacks[_id - 1];
        
        return (
            attack.id,
            attack.timestamp,
            attack.email,
            attack.userId,
            attack.ipAddress,
            attack.country,
            attack.attackType,
            attack.confidence,
            attack.bertProbability,
            attack.bertUsed,
            attack.loginSuccessful,
            attack.blockNumber,
            attack.logger
        );
    }
    
    // Fonction simplifiée pour récupérer les infos principales
    function getAttackBasic(uint256 _id) public view returns (
        uint256 id,
        string memory email,
        string memory attackType,
        uint256 confidence,
        uint256 blockNumber
    ) {
        require(_id > 0 && _id <= attackCount, "Invalid attack ID");
        AttackEvent memory attack = attacks[_id - 1];
        
        return (
            attack.id,
            attack.email,
            attack.attackType,
            attack.confidence,
            attack.blockNumber
        );
    }
}
