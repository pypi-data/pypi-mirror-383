import os
import json
import tqdm
import yaml
import typer
from pathlib import Path
from typing import List
from shutil import copytree
from typing import cast

def get_lambda_dirs_with_endpoint(base_path: Path) -> List[str]:
    result = []
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"La ruta base no existe: {base_path}")

    for entry in os.listdir(base_path):
        dir_path = os.path.join(base_path, entry)
        endpoint_file = os.path.join(dir_path, "endpoint.yaml")
        if os.path.isdir(dir_path) and os.path.isfile(endpoint_file):
            result.append(entry)

    return result

def get_api_initial_definition(dir_name: Path):
    with open(dir_name, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_api_config(lambdas_path: Path):
    endpoint_dirs = get_lambda_dirs_with_endpoint(lambdas_path)
    import_lambdas = []
    endpoint_list = []
    for dir_name in endpoint_dirs:
        import_lambdas.append(f"from src.lambdas.{dir_name}.lambda_function import lambda_handler as {dir_name}_handler")

        with open(Path(lambdas_path / dir_name / "endpoint.yaml"), 'r', encoding="utf-8") as f:
            endpoint_list.append({"definition": yaml.safe_load(f), "name": dir_name})

    return import_lambdas, endpoint_list

def build_api_config(lambdas_path: Path, environment: str = None, app_name: str = None, aws_account: str = None, aws_region: str = None):
    endpoint_dirs = get_lambda_dirs_with_endpoint(lambdas_path)
    endpoint_list = []
    for dir_name in endpoint_dirs:

        with open(Path(lambdas_path / dir_name / "endpoint.yaml"), 'r', encoding="utf-8") as f:
            endpoint_node = cast(dict, yaml.safe_load(f))
            for endpoint_name in endpoint_node.keys():
                for method in endpoint_node[endpoint_name]:
                    if 'x-amazon-apigateway-integration' in endpoint_node[endpoint_name][method]:
                        integration = endpoint_node[endpoint_name][method]['x-amazon-apigateway-integration']
                        if 'uri' in integration and environment is not None:
                            integration['uri'] = f'arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{aws_region}:{aws_account}:function:{environment}-{app_name}-{dir_name}/invocations'
                        if 'credentials' in integration and environment is not None:
                            integration['credentials'] = f'arn:aws:iam::{aws_account}:role/{environment}-{app_name}-apigw-invoke-lambda-role'
            endpoint_list.append(endpoint_node)

    return endpoint_list

def build_lambdas(lambdas_path: Path, build_path: Path):
    """
    Copia toda la estructura de src/lambdas a infra/components/lambdas,
    manteniendo la jerarquía de carpetas.
    """

    # Crear destino si no existe
    build_path.mkdir(parents=True, exist_ok=True)

    # Iterar sobre cada subcarpeta dentro de src/lambdas
    for lambda_dir in tqdm.tqdm(lambdas_path.iterdir()):
        if lambda_dir.is_dir():
            target = build_path / lambda_dir.name
            # copytree falla si ya existe el destino → usamos dirs_exist_ok
            copytree(lambda_dir, target, dirs_exist_ok=True)
            typer.echo(f"Copiado {lambda_dir} → {target}")


def build_lambda_stack(build_lambdas_path: Path, environment: str, app_name: str):
    lambdas_init = build_lambdas_path / "__init__.py"

    excluded_dirs = [
        "__pycache__"
    ]

    for lambda_dir in tqdm.tqdm(build_lambdas_path.iterdir()):
        if lambda_dir.is_dir() and lambda_dir.name not in excluded_dirs:
            typer.echo(f"Procesando {lambda_dir.name} para __init__.py")

            lambda_camel_case = lambda_dir.name.replace("-", "_").title().replace("_", "")

            infra_config = ""
            with open(lambdas_init, "r") as f:
                infra_config = f.read()

            with open(lambdas_init, "a") as f:
                header = f"############ Lambda{lambda_camel_case}Stack ############"
                if header in infra_config:
                    typer.echo(f"Sección {header} ya existe en __init__.py, se omite.")
                    continue
                f.write(f"""
        {header}
        from .{lambda_dir.name}.infra_config import Lambda{lambda_camel_case}Stack

        Lambda{lambda_camel_case}Stack(
            name="{environment}-{app_name}-{lambda_camel_case}Stack",
            environment="{environment}",
            app_name="{app_name}",
            lambda_execution_role_arn=lambda_execution_role_arn,
            layers=layers,
            sg_ids=sg_ids,
            subnets_ids=subnets_ids,
            tags=DEFAULT_TAGS
        )\n\n""")

def build_api(api_path: Path, lambdas_path: Path, output_file: Path):
        
    api_definition = get_api_initial_definition(api_path)
    endpoint_list = build_api_config(
        lambdas_path,
        environment=os.getenv("ENVIRONMENT") or "dev",
        app_name=os.getenv("APP_NAME") or "myapp",
        aws_account=os.getenv("AWS_ACCOUNT_ID") or "123456789012",
        aws_region=os.getenv("AWS_REGION") or "us-east-1"
    )

    for ep in endpoint_list:
        try:
            ep_path = list(ep.keys())[0]
        except Exception as e:
            typer.echo(f"[!] Error al procesar endpoint: {e}", color=typer.colors.RED)
            continue
        if ep_path in api_definition['paths']:
            ep_methods = list(ep[ep_path].keys())
            for ep_method in ep_methods:
                if ep_method in api_definition['paths'][ep_path]:
                    typer.echo(f"[!] La ruta '{ep_path}' con método '{ep_method}' ya existe en la definición OpenAPI. Se omitirá.")
                else:
                    cast(dict, api_definition['paths'][ep_path]).update({ep_method: ep[ep_path][ep_method]})
        else:
            cast(dict, api_definition['paths']).update(ep)

    with open(output_file, "w+", encoding="utf-8") as f:
        json.dump(api_definition, f, indent=2)
