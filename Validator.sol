pragma solidity >=0.4.22 <0.6.0;
contract Validator {
    address owner;
    mapping(bytes32 => uint) numDocuments;
    mapping(bytes32 => mapping(bytes32 => bool)) internal patientDocs;
    
    constructor() public {
        owner = msg.sender;
    }
    
    function showOwner() public view returns (address _owner) {
        return owner;
    }
    
    function hashString(string memory str) private pure returns (bytes32 hash){
        return keccak256(bytes(str));
    }

    function addDocument(string memory email, bytes32 documentHash) public {
        require(owner == msg.sender);
        bytes32 emailHash = hashString(email);
        increaseDocumentCount(emailHash);
        patientDocs[emailHash][documentHash] = true;
    }
    
    function increaseDocumentCount(bytes32 user) private {
        numDocuments[user]++;
    }
    
    function validate(bytes32 emailHash, bytes32 documentHash) 
            private view returns(bool valid) {
        return patientDocs[emailHash][documentHash];
    }
    
    
    function validateAll(string memory email, bytes32[] memory documents)
            public view returns(bytes32[] memory validated) {
        bytes32 emailHash = hashString(email);
        uint documentCount = numDocuments[emailHash];
        require(documents.length == documentCount);
        bytes32[] memory validatedDocuments = new bytes32[](documents.length);
        for(uint i = 0; i < documents.length; i++){
            if(validate(emailHash, documents[i])) {
                validatedDocuments[i] =  documents[i];
            }
        }
        if(validatedDocuments.length == 0){
            validatedDocuments = new bytes32[](0);
        }
        //return validatedDocuments;
        return validatedDocuments;
        }
   
}