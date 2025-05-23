# Contributing

Thank you for considering contributing to this project! We welcome contributions to improve this project.
For general contribution and community guidelines, please see the [community repo](https://github.com/cyberark/community).

Go over this guide to learn how to contribute to the project. 

## General Steps for Contributing

1. Fork the project.  
1. Clone your fork.  
1. Make local changes to your fork by editing files.
1. Run all checks successfully.
1. Commit your changes.  
1. Push your local changes to the remote server.  
1. Create a new Pull Request.  

From here, your pull request will be reviewed, and once you've responded to all feedback, it will be merged into the project. Congratulations, you're a contributor!

## Development

Go over the [developer's guide](https://cyberark.github.io/simple-llm-eval/developers/dev-notes/) according to the type of contribution you want to make.

## Testing

* Continually make sure that tests are passing: `pytest -v tests`
* Run the pre-PR script: `ci/pre_pull_request_checks.py` to run all checks before you create 
a PR. This includes linters, unit tests coverage, etc.
* If you made changes to `reports-frontend`, also run `ci/pre_pull_request_checks_react.py`

## Documentation

Make sure to update the documentation as needed.

## Releases

Releases are handled by the CI pipeline after a successful approval and merge to the main branch.

## Legal
Any submission of work, including any modification of, or addition to, an existing work ("Contribution") to “simple-llm-eval" shall be governed by and subject to the terms of the Apache License 2.0 (the "License") and to the following complementary terms. In case of any conflict or inconsistency between the provision of the License and the complementary terms, the complementary terms shall prevail. By submitting the Contribution, you represent and warrant that the Contribution is your original creation and you own all right, title and interest in the Contribution. You represent that you are legally entitled to grant the rights set out in the License and herein, without violation of, or conflict with, the rights of any other party. You represent that your Contribution includes complete details of any third-party license or other restriction associated with any part of your Contribution of which you are personally aware.
