# Building a front-end environment

## Fix members_card.js

In front > members_card.js, there is a value that needs to be changed for each environment, so modify that value.  
There are two points to be modified:
1. const API_GATEWAY_URL = "The APIGateway URL displayed when deploying in [Building the Backend > Deploying the Membership Card Application (APP)]"
1. const liffId = "LIFFID of the LIFF app you added in [Create LINE Channel > Create Channel > Add LIFF App]"

## Deploy front-end modules in S3

 Place all the files in the front folder into the target S3 bucket created in the backend construction procedure.


[Next page](test-data-charge.md)  

[Back to Table of Contents](README_en.md)
