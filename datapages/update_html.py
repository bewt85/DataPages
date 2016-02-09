import logging
import os

from jinja2 import Environment, FileSystemLoader

from .common import species_filename, get_config, DomainConfig

logger = logging.getLogger(__name__)

def get_template():
    datapages_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(datapages_dir)
    templates_dir = os.path.join(parent_dir, 'templates')
    loader = FileSystemLoader(templates_dir)
    env = Environment(loader=loader)
    index_template = env.get_template('index.html')
    logger.info('Using index.html template from %s' % templates_dir)
    return index_template

def write_domain_index(species_list, output_dir, domain_config):
    domain_name = domain_config.domain_name
    def species_url(species):
        return "data/%s" % species_filename(species)
    species_urls = {species: species_url(species) for species in
                    species_list}
    index_path = os.path.join(output_dir, domain_name, 'index.html')
    content = get_template().render(
        species_urls=species_urls,
        domain_title=domain_config.domain_title,
        domain_description=domain_config.render_domain_description()
    )
    with open(index_path, 'w') as index_file:
        logger.info("Writing index page for %s to %s" % (domain_name, index_path))
        print(content, file=index_file)
