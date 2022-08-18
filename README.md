# DTCD Workspaces

[Complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop) plugin for workspaces management.

## Installation

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

- Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest/).

### Install from Nexus

For this plugin, you can get the latest build from Nexus or [GitHub Release page](https://github.com/ISGNeuroTeam/complex_rest_dtcd_workspaces/releases):
* Download the archive with the latest build.
* Unpack the archive into `complex_rest/plugins` directory.
* [Create initial records](#database-initialization-script).

### Install via Make

* Clone the Git repository
    ```sh
    git clone git@github.com:ISGNeuroTeam/complex_rest_dtcd_workspaces.git
    ```
* Run the following from inside the repository root (you'll get the same archive as in Nexus):
    ```sh
    make pack
    ```
* Unpack the archive into `complex_rest/plugins` directory.
* [Create initial records](#database-initialization-script).

### Install manually

If you are a developer, then follow this section.

* Clone the Git repository into `plugin_dev/` directory:
    ```sh
    git clone git@github.com:ISGNeuroTeam/complex_rest_dtcd_workspaces.git
    ```
* Copy configuration files from `docs/` to `dtcd_workspaces/` with the following command:
    ```sh
    cp docs/dtcd_workspaces.conf.example  dtcd_workspaces/dtcd_workspaces.conf
    ```
* Create virtual environment
    ```sh
    python -m venv venv
    ```
* Activate virtual environment and install the requirements:
    ```sh
    source venv/bin/activate
    pip install -r requirements.txt
    ```
* Make a **symlink** for `./dtcd_workspaces/dtcd_workspaces` in `complex_rest/plugins` directory.
* Run custom Django command from project directory to [create initial records for Role Model](#creating-initial-records).
    ```bash
    python complex_rest/manage.py create_root_records
    ```

## Deployment

For deployment we need to get a build archive - see the previous section on how to do that. Then:

* Stop `complex_rest`.
* Unpack the archive into `complex_rest/plugins` directory.
* [Create initial records](#database-initialization-script).
* Start `complex_rest`.

## Notes

### Creating initial records

The plugin has `create_root_records` custom Django command which prepares Role Model tables in the database.

### Database initialization script

There is a helper script `database_init.sh` that will set up the database for you.

You can run it from anywhere you like:

```bash
./database_init.sh
```

## Running the tests

Run all tests from project's root directory:
```bash
python ./complex_rest/manage.py test \
    ./plugin_dev/dtcd_workspaces/tests \
    --settings=core.settings.test
```

## Built With

* [Django](https://docs.djangoproject.com/en/3.2/) - The web framework used


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

- Ilia Sagaidak (isagaidak@isgneuro.com)


## License

[OT.PLATFORM. License agreement.](LICENSE.md)

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration