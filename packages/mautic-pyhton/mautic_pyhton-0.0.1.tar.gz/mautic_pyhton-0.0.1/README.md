# Mautic Client

A python client for Mautic API

## Installation

You can currently install project via github:

```pip install git+https://github.com/iamafasha/mautic-pyhton.git#egg=mautic```

## Usage

```
from src.mautic.client import Client

client = Client("https://mautic.test").basic_auth("admin", "admin_password")

contacts = client.contacts.get()
print(contacts)

```

## Supported APIs
### Supported APIs

<table style="width:100%">
  <tr>
    <th>API Endpoint</th>
    <th>Supported</th>
  </tr>
  <tr>
    <td>Contacts</td>
    <td>get contacts, get contact, create contact, batch create contacts, update contact, batch update contacts, delete contact, batch delete contacts</td>
  </tr>
  <tr>
    <td>Campaigns</td>
    <td>add contact, remove contact</td>
  </tr>
  <tr>
    <td>Segments</td>
    <td>get segments, get segment, create segment, update segment, delete segment, add contact, remove contact</td>
  </tr>
</table>


## Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit counts, from documentation to issue reports and pull requests.

You can contribute in several ways:

### Reporting Bugs

If you find a bug, please report it to the [issue tracker](https://github.com/iamafasha/mautic-pyhton/issues).

### Fixing Bugs

Look through the [issue tracker](https://github.com/iamafasha/mautic-pyhton/issues) for bugs. Pick one that interests you, and try to fix it.

### Adding New Features

If you have a feature request, please file an issue in the [issue tracker](https://github.com/iamafasha/mautic-pyhton/issues). If your feature request is accepted, you can start working on it.

### Writing Documentation

Mautic Pyhton could always use more documentation. If you see a place where the documentation is lacking, please add to it! You can also add more examples to the documentation.

### Submitting Changes
Once you've made your changes, please submit a pull request to the [Mautic Pyhton repository](https://github.com/iamafasha/mautic-pyhton/pulls).

Please make sure that your pull request is well tested and follows the coding standards of the rest of the project.


### Code of Conduct

Please make sure that you follow the [Code of conduct](https://github.com/iamafasha/mautic-pyhton/blob/master/CODE_OF_CONDUCT.md) when interacting with the project.
