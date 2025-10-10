# edubaseid/cli.py
"""
CLI tools for EduBaseID SDK.
"""

import click

from .client import EduBaseIDClient

@click.group()
def cli():
    """EduBaseID CLI tools."""
    pass

@cli.command()
def login():
    """Perform login via CLI."""
    client = EduBaseIDClient()
    url = client.get_authorize_url()
    click.echo(f"Open: {url}")
    code = click.prompt("Enter code from callback")
    token = client.exchange_code_for_token(code)
    click.echo(f"Token: {token['access_token']}")

@cli.command()
def validate_client():
    """Validate client config."""
    client = EduBaseIDClient()
    result = client.validate_client()
    click.echo(result)

@cli.command()
@click.option('--name', prompt='App name')
@click.option('--redirect-uri', prompt='Redirect URI')
def register_app(name, redirect_uri):
    """Register new app."""
    client = EduBaseIDClient()
    access_token = click.prompt("Access token")
    result = client.register_application(name, redirect_uri, access_token=access_token)
    click.echo(result)

@cli.command()
@click.option('--user-id', prompt='User ID')
def get_user(user_id):
    """Get user info."""
    client = EduBaseIDClient()
    access_token = click.prompt("Access token")
    user = client.get_user_info(access_token)
    click.echo(user)