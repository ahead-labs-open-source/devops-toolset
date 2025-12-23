# Project Title

One Paragraph of project description goes here

## Getting Started

This is a WordPress project based on [devops-toolset](https://github.com/aheadlabs/devops-toolset/).  
This means that **only customizations** are pushed to the repository. Any file that can be generated programatically is
excluded.  
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You need Python 3.8.2+ installed on your machine. Please follow the instructions on the [Python web site](https://www.python.org/downloads/).

### Installing

Clone this repository using the following command:

```
git clone <repository URL>
```

Execute the **wordpress/bootstrap_existing_repository.py** script from the devops-toolset project using the root directory as the **project_path**. 

```
python <devops-toolset path>/wordpress/bootstrap_existing_repository.py <root path> <other arguments>
```


## Running the tests

### Unit tests

We do not have unit tests at this time.

### End to end tests

We do not have end to end tests at this time.

## Deployment

You will need a DevOps platform to pack and deploy this website.  
Please refer to the [WordPress section of the devops-toolset project](https://github.com/aheadlabs/devops-toolset/#wordpress-tools) for information on the tools provided there.

## Versioning

We use [SemVer](http://semver.org/) for versioning. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

