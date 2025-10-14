#!/usr/bin/env python3
import click
from jinja2 import BaseLoader, Environment
import tempfile
import crossplane
import os

from nginx_config_lint.constants import ALLOWED_NGINX_DIRECTIVES, SUPPORTED_NGINX_DIRECTIVES_WIKI_LINK


def _parse_nginx_config(nginx_config):
    config_tmp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')

    config_tmp_file.write('http {\n' + nginx_config + '\n}\n')
    config_tmp_file.close()

    config = crossplane.parse(config_tmp_file.name)

    if config['status'] != 'ok':
        error_lines = " | ".join(f"🚨 [line {e['line']}]: {e['error']}" for e in config['errors'])
        raise RuntimeError(f'Ошибки парсинга nginx конфига:\n{error_lines}\n💡 Проверьте синтаксис файла.')

    if not config['config']:
        raise RuntimeError("Missing config after parsing")

    if len(config['config']) > 1:
        raise RuntimeError("Multiple config after parsing")

    parsed = config['config'][0]['parsed']

    if not parsed or not parsed[0].get('block'):
        error_lines = ' | '.join(f"🚨 [line {e['line']}]: {e['error']}" for e in config['errors'])
        raise RuntimeError(f"Parsing failed. {error_lines}")

    return parsed[0]['block']


def _traverse_ast_block(directives):
    for directive_block in directives:
        directive = directive_block['directive']

        if directive not in ALLOWED_NGINX_DIRECTIVES:
            return {
                'line': directive_block['line'],
                'text': f'{directive} {' '.join(directive_block["args"])}',
            }

        if directive == 'location':
            result = _traverse_ast_block(directive_block['block'])

            if result is not None:
                return result

    return None


def _nginx_directives_lint(nginx_config):
    parsed_nginx_config = _parse_nginx_config(nginx_config)

    for directive_block in parsed_nginx_config:
        if directive_block['directive'] != 'server':
            continue

        result = _traverse_ast_block(directive_block["block"])

        if result is not None:
            raise RuntimeError(
                f'Обнаружена не поддерживаемая директива Nginx! Line: {result.get("line")}: "{result.get("text")}". Список поддерживаемых директив можно найти {SUPPORTED_NGINX_DIRECTIVES_WIKI_LINK}')


class SkipMissingLoader(BaseLoader):
    def get_source(self, environment, template):
        try:
            with open(os.path.join('nginx', template), "r") as f:
                source = f.read()
            return source, None, lambda: True
        except FileNotFoundError:
            # Return empty content for missing templates
            return "", None, lambda: True


@click.command()
@click.argument('files', nargs=-1)
def main(files):
    """CLI tool to lint nginx config templates"""

    options = [
        {'template': 'pr.conf',
         'params': {'service_environment': 'dev', 'workflow_name': 'pr', 'service_key': 'my-awesome-service',
                    'pr': {'number': 123, 'suffix': '',
                           'type_key': 'services'}}},
        {'template': 'dev.conf',
         'params': {'service_environment': 'dev', 'workflow_name': 'dev', 'service_key': 'my-awesome-service'}},
        {'template': 'dev.conf',
         'params': {'service_environment': 'ift', 'workflow_name': 'release', 'service_key': 'my-awesome-service'}},
        {'template': 'dev.conf', 'params': {'service_environment': 'pre-prom', 'workflow_name': 'release',
                                            'service_key': 'my-awesome-service'}},
        {'template': 'dev.conf',
         'params': {'service_environment': 'prom', 'workflow_name': 'release', 'service_key': 'my-awesome-service'}},
    ]

    for option in options:
        config = render_config_template(option)

        if not config:
            continue

        try:
            _nginx_directives_lint(config)
            click.echo(
                f'✅  {click.style(option['template'], fg='green')} with {click.style(option['params']['service_environment'], fg='red')} Environment verified')
        except Exception as e:
            click.echo(e)
            click.echo(
                f'Config file: {click.style(option['template'], fg='green')}, Environment: {click.style(option['params']['service_environment'], fg='red')}')
            exit(1)


def render_config_template(option):
    try:
        loader = SkipMissingLoader()
        env = Environment(loader=loader)
        template = env.get_template(option['template'])
        return template.render(option['params'])
    except Exception as e:
        click.echo(f"Error rendering template: {e}", err=True)


if __name__ == '__main__':
    main()
