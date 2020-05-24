# Hyperion - Distributed Ledger Healthcare System

## Project Scope

The aim of the project is to develop a distributed healthcare system that allows patients to store their personal encrypted data on their own device and share it when needed.

It will also allow healthcare professionals to request patient information and store further information pertaining to a patient which upon completing the session will be removed from their access.

The project started in September 2019 and finished in May 2020.

The main components of the system will be comprised of:

- A private Ethereum network set up on multiple IoT devices
- A smart contract and a web3 RESTful API
- A DApp to be used by the healthcare professionals
- A mobile phone application to be used by the patient
- A physical NFC enabled check-in system (not implemented yet, this was replace by a digital check-in function on the mobile lication)

For any questions around the project please get in touch.

## Related Repositories

- [Hyperion Android Application](https://github.com/stefdworschak/hyperion_mobile_app) 
  - APK: [Download here](http://dworschak-media.com/Hyperion.apk)
  - IMPORTANT! Don't use any real personal data since anybody with demo access will be able to see it.
- [Hyperion Web Application](https://github.com/stefdworschak/hyperion)
  - Deployed at: [hyperion-health.com](https://www.hyperion-health.com)
  - Demo user: `demo`
  - Demo password: `fakepassword`
- [Hyperion Smart Contract API](https://github.com/stefdworschak/hyperion_contract_api)
  - Copy Solidity contract from [Validator.sol](https://github.com/stefdworschak/hyperion_contract_api) to [Remix](https://remix.ethereum.org/) to test (max. compiler version 0.5.17)

## Project Presentation Video

<a href="http://www.youtube.com/watch?feature=player_embedded&v=geCpzzMY-RQ
" target="_blank"><img src="https://i.ibb.co/6gP1N8q/Title-Screen.png"
alt="Project Video Thumbnail" width="60%" /></a>

## Technologies

### Java/Android

The Hyperion Patient mobile is developed in Java/Android.

The deciding factor to use Android/Java was the good integration with Google technologies (such as Firebase) which would be used for the implementation.

The second deciding factor to go with an Android as opposed to only having a cloud application was the fact that the Patient data is stored on the device which is much easier to be handled by an Android application.

### Python/Django

The Hyperion web application for Healthcare Professionals uses Python’s Django framework as dedicated development solution. All logic and static files are served by the Django framework utilizing many of its native implementations such as user management.

### Symmetric Encryption

The mobile and the web application will use Symmetric Encryption (AES) algorithms to encrypt, share and decrypt data from the mobile to the web application.

### Raspberry Pi and Distributed ledger technologies

The private Ethereum distributed ledger deployed on IOT devices (here a Raspberry PI) uses the geth CLI utility tool to create the distributed ledger, new nodes and monitor the network traffic. The Distributed ledger also has a Solidity smart contract deployed to it which is used to store and validate document hashes.

The Raspberry PI also acts as device to run a Python Flask app as API to interact with the smart contract.

## AWS EC2 Server, Apache2 and Letsencrypt

The web application is deployed on an AWS EC2 instance and is served using Apache2 HTTP server over HTTPS only using a SSL certificate from Letsencrypt.

## Use Cases

<img src="https://i.ibb.co/b5JsxSn/Hyperion-Use-Case.png"
alt="Use Case Diagram" width="60%" />

### 1 Patient user type

#### 1.1 Ability to create a new account

A first-time user of the application should have the ability to create a new account, enter some personal information about themselves and create a new 2-factor authentication 

#### 1.2 Ability to log into their account

An already registered user should have the ability to log into their created account with a password in order to retrieve all the information pertaining to the user.

#### 1.3 Ability to edit personal information

An already registered user should have the ability to change any of the personal information they previously entered in order to keep their record up to date, change their password or create a new 2-factor authentication code

#### 1.4 Ability to check-in at healthcare facility

An already registered user should have the ability to check-in at a healthcare facility. This should be as accessible as possible and should not slow them down in any considerable fashion. The most seamless option would be through a tap of the mobile phone against an NFC interface. However, not all users will have NFC enabled phones or might check-in just before arrival so a check-in via healthcare facility search or selection function is a possible consideration as well.

#### 1.5 Ability to see their own patient history

An already registered user should have the ability to view any records that have been created on their behalf. These records should be securely stored and only upon explicit permission they should be able to be viewed by even a healthcare professional.

#### 1.6 Ability to revoke access to any information

An already registered user should have the ability to revoke access to any of their personal or medical information at any point in time to guarantee their data privacy.

### 2 Healthcare Professional user type

#### 2.1 Ability to get access to patient data

An already registered user should have the ability to gain access to patient’s personal data and their patient history to triage, make an informed decision or diagnosis.

#### 2.2 Ability to add new Patient record

An already registered user should have the ability to add a new patient record whether it is just a note, a diagnosis, write a prescription or a referral to a specialist. As part of adding the Patient Record a follow-up appointment must be scheduled before finishing the session.
