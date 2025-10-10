
from pathlib import Path

from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration

if __name__ == "__main__":

    # Configure the docs
    config = GenerationConfiguration(
        minify=False,
        copy_css=True,
        copy_js=True,
        expand_buttons=True,
        show_breadcrumbs=False,     # True doesn't seem to work
        show_toc=True,
        collapse_long_descriptions=True,
        collapse_long_examples=True,
        description_is_markdown=True,
        examples_as_yaml=True,
        link_to_reused_ref=True,    # Should we do this or duplicate the entry?
        deprecated_from_description=True,
        template_md_options={
        #     "badge_as_image": True,
            "show_heading_numbers": True
        },
        # template_name="md_nested"
        custom_template_path="jsfh_template/base.html"
    )

    config.schema_title=False

    # Using the json file and config from above, create the docs web page
    base_path = Path(__file__).parent.parent

    # Generate the plant schema html
    schema_html_path = Path("_static/plant_schema.html")
    generate_from_filename(
        base_path / "windIO" / "schemas" / "plant" / "wind_energy_system.yaml",
        schema_html_path,
        config=config
    )

    # Generate the turbine schema html
    schema_html_path = Path("_static/turbine_schema.html")
    generate_from_filename(
        base_path / "windIO" / "schemas" / "turbine" / "turbine_schema.yaml",
        schema_html_path,
        config=config
    )
