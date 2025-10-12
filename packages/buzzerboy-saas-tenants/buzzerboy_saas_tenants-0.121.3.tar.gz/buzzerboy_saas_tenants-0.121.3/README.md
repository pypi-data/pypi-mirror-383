# Buzzerboy SaaS Tenants

Buzzerboy SaaS Tenants is a package that provides components for managing tenant configurations in a multi-tenant SaaS application. This package helps in defining and managing tenant-specific settings, data isolation, and other tenant-related functionalities across various applications.

It implements Buzzerboy's Standard Features by default, and isolate the UI separately. Applications that are developed that will
use Buzzerboy Standard Features can implement UI separately.

More information:
https://buzzerboy.atlassian.net/wiki/spaces/BC/pages/69369878/Standard+Features

## Introduction

The Buzzerboy SaaS Tenants package is designed to simplify the management of tenant configurations in a multi-tenant SaaS environment. It provides a set of tools and components that allow developers to easily define and manage tenant-specific settings, ensuring data isolation and customization for each tenant.

## Features

- Tenant configuration management
- Data isolation for tenants
- Tenant-specific settings and customization
- Easy integration with existing applications

## Reference
The `buzzerboy-saas-tenants` package uses the following Buzzerboy guidances:
- https://buzzerboy.atlassian.net/wiki/spaces/BC/pages/226820115/How+To+Build+an+app+as+a+reusable+component
- https://buzzerboy.atlassian.net/wiki/spaces/BC/pages/123207703/Creating+and+Distributing+a+Modular+Reusable+Django+App

## Getting Started

Follow these steps to get started with the Buzzerboy SaaS Tenants package:

### Installation

To install the package, use the following command:

```sh
pip install buzzerboy-saas-tenants
```

###Software Dependencies
Ensure you have the following dependencies installed:

- Python >= 3.8
- Django >= 3.2
- djangorestframework >= 3.12


### Usage
To use `buzzerboy-saas-tenants` you must include it in your django app under the requirements.txt, and add each component as an installed app. 

More details on Confluence:
https://buzzerboy.atlassian.net/wiki/spaces/BC/pages/225968137/How+To+Use+buzzerboy-saas-tenants

##Latest Releases
Check the releases page for the latest updates and release notes.

##API References
Refer to the API documentation for detailed information on how to use the package.

##Build and Test
To build and test the package, follow these steps:

###Prepare
Before building, prepare the build by determining the build version and generating a CHANGELOG by analyzing commits
```sh
python prepare.py
```

##Building
Use the following command to build the package:
```sh
python -m build
```

Testing
Run the tests using the following command:
```sh
pytest
```

##Contribute
All Buzzerboy Platform members (Staff, Contractors, Clients and Users) are welcome contributions from the community to make this package better. Here’s how you can contribute:

1. Clone the repository
2. Create a new branch (git checkout -b feature-branch)
3. Make your changes
4. Commit your changes (git commit -am 'Add new feature')
5. Push to the branch (git push origin feature-branch)
6. Create a new Pull Request
7. For more details, refer to our contributing guidelines.

###License
This project is licensed under the MIT License - see the LICENSE file for details.

###Acknowledgements
- Django
- Django REST framework