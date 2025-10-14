### How to add new custom tools

- install gptsre-tool decorator lib: `pip install gptsre-tools --extra-index-url https://pypi.shopee.io`
- add your tools under `tools` directory, follow the tool examples (don't modify this folder name)
- modify `setup.py` accordingly
  - Note: 
    - the `package_name` should be the same with the `package_data` folder

- we also support ENV injection that later can be configured through GPTSRE platform. see code example in [GetAuthorDummyTool](shopee_pfms_smart_tools/tools/get_resume_parse.py) | for more info refer to this [Confluence Guide](https://confluence.shopee.io/pages/viewpage.action?pageId=2594301632#id-[GPTSRE][Platform]CustomToolsProvisioning(AddNewTools)-HowtoInjectENVvariablebeforetoolsimported)

- To register the tools, use this decorator `@ToolRegistry.register_tool(<tool_namespace_name>, <args_input_schemas>, **init_args)`
- **DON'T modify any loguru configuration** as will affecting the platform it self. Just use it by importing it `from loguru import logger`
- If you want to init parent class, use implicit `super()`. DON'T use explicit `super(type, obj)` because can cause issue when reloading the module.
- Note: `setup.py` for package name please use underscore only ex: `gptsre_tool_examples` same as your folder name
  ```
  def _setup():
    with cd(PROJECT_DIR):
        # specify additional required packages
        install_requires = [
            # for this particular package
            # no need to specify as gptsre platform already have it
            # 'gptsre-tools',
        ]
        setup(
            name='gptsre_tool_examples', # MAKE SURE package name use underscore only, Don't use "-"
            version='0.0.8',
            author='Shopee',
            author_email='achmad.akbar@shopee.com',
            description='Examples Custom GPTSRE Tools',
            url='https://git.garena.com/achmad.akbar/gptsre_tool_examples',
            packages=find_packages(),
            install_requires=install_requires,
            package_data={
                'gptsre_tool_examples': [ # MAKE SURE same as your folder name, Only use under_score "_", don't use "-"
                    'gptsre_tool_examples/*',  # MAKE SURE same as your folder name, Only use under_score "_", don't use "-"
                ],
            },
            include_package_data=True,
        )
  ```

### How to test tool before upload

Link for more comprehensive guide: [Confluence Guide - How to test tool before upload](https://confluence.shopee.io/pages/viewpage.action?pageId=2594301632#id-[GPTSRE][Platform]CustomToolsProvisioning(AddNewTools)-Howtoverify(invoke)Toolswithoutuploadthepackage
)
- install package `pip install gptsre-tools`
- make sure we are on package directory
  - for this repo should be on the parent directory
  ```
    ├── shopee_pfms_smart_tools
    │   ├── __init__.py
    │   ├── main.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-311.pyc
    │   │   └── main.cpython-311.pyc
    │   └── tools
    │       ├── get_resume_parse.py
    │       ├── __init__.py
    │       └── __pycache__
    ├── __init__.py
    ├── README.md
    ├── setup.cfg
    └── setup.py
  ```
- run `gptsre-tool-checker` or by specifying all the arg param see `gptsre-tool-checker --help` for more info or confluence page above.
- follow along the prompt in the cli
  - `Enter package name: ` fill in our new package name (ex: gptsre_tool_examples)


### How to upload the tool package and provision in GPTSRE Platform

[Please follow this guide](https://confluence.shopee.io/pages/viewpage.action?pageId=2594301632)
