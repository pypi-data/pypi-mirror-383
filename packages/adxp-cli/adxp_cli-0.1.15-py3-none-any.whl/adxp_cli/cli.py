import click
from adxp_cli.agent.cli import agent
from adxp_cli.auth.cli import auth
from adxp_cli.model.cli import model
from adxp_cli.model.cli_v2 import cli_v2 as model_v2
from adxp_cli.finetuning.cli import finetuning
from adxp_cli.finetuning.cli_v2 import cli_v2 as finetuning_v2
from adxp_cli.apikey.cli import apikey
from adxp_cli.prompts.cli import prompts
from adxp_cli.authorization.cli import authorization
from adxp_cli.dataset.cli import cli as dataset


@click.group()
def cli():
    """Command-line interface for AIP server management."""
    pass


cli.add_command(auth)
cli.add_command(agent)
cli.add_command(model)
cli.add_command(model_v2, "model-v2")
cli.add_command(finetuning)
cli.add_command(finetuning_v2, "finetuning-v2")
cli.add_command(apikey)
cli.add_command(prompts)   
cli.add_command(authorization, "authorization")
cli.add_command(authorization, "authz")
cli.add_command(dataset, "dataset")


if __name__ == "__main__":
    cli()
