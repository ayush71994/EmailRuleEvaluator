## Dependencies

pip install google-api-python-client google-auth-oauthlib mysql-connector-python

Run Db/001.sql in mysql cluster for setting up the schema for storing emails

## High level Components

We have two major components 
- Mail Fetcher 
- Rule Evaluator

### Mail Fetcher

Mail fetcher hosts the logic for integrating with gmail api and fetching the emails.
It also has the logic for connecting with database and storing the mails fetched.
It uses 'credentials.json' to authenticate the gmail api and stores the token in the same directory for future uses.

To download credentials.json, please perform the following
- Login to google cloud console
- Create a project 
- Go to Gmail api and create credentials
- Go to credentials and then download

Once downloaded update the credentials.json file provide and run **mail_fetcher.py**.

Once the script is run, the mails would be fetched and stored in the DB.

### Rule Evaluator

This component fetches the mails stored and evaluates the rules based on a config defined in rules.json. After evaluation it would print the expected action to be taken for each email.

Define rules in the rules.json file 
Run the **rule_evaluator.py**


### Rules.json config

This is our template for defining rules for email matching.

The rules.json config defines a list of rule groups which can be evaluated for each email. The priority of rule group is currently determined by the order of where its present in the json file.

Each rule group can have the following components
- 'group_predicate' - The predicate to be applied on the all the rules defined in the group. Possible values 'ALL' and 'ANY'
- 'rules' - List of rules to be evaluated as part of this group. The result of each rule would be used for the evaluation of final rule_group result
- 'actions' - Actions to be taken if the rule group evaluation returns true

For defining individual rules we have the following components
- 'field' - field in the email which would be used for evaluation. Can be 'subject', 'received_at', 'sender' etc
- 'predicate': Condition to be evaluated. Can contains, less than, more than etc
- 'value': Value to check the 'field' for evaluation

