# NTP Facade SMR

[![PyPI version](https://badge.fury.io/py/ntp-facade-smr.svg)](https://badge.fury.io/py/ntp-facade-smr)

A simple Python library that provides a clean, user-friendly facade for synchronizing a client's clock with a specified NTP server.

This package is designed to make NTP time synchronization straightforward by abstracting away the low-level details of the protocol. It is ideal for applications on devices like IMUs, cameras, or any client that needs to ensure its data has an accurate timestamp.

## Features

* **Simple Interface**: Get synchronized time with a single method call.
* **Facade Design Pattern**: Hides the complexity of NTP communication.
* **Custom Server Support**: Easily point the client to your own NTP server (e.g., a local server on your network).
* **Error Handling**: Raises clear exceptions on network failures or timeouts.

## Installation

You can install the package from PyPI:

```bash
pip install ntp-facade-smr