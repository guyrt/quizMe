# Backend/Python testing: 
All backend and python code should be tested using the pytest framework, which offers several advantages over python unittest or the django tet frameworkk.
## Test Principles: 
- Make use of fixtures to handle repeated steps. They are hierarchically inherited and can be overriden if needed. 
- Whenever possible don't use example data in a database for testing. Rely on mixer/faker to generate fake data, or seed in fake data via fixtures. 
- Test the code, not the framework. (Don't test that django does django stuff, django already does that)

## Running Pytest: 
- In pycharm there should be a run config called "pytest in test" that will work properly
- To directly run: 
```shell
docker compose up -d  &
sleep 5 
CONTAINER_ID=$(docker ps | grep web | awk '{print $1}')
docker exec -it ${CONTAINER_ID} bash 
```
once the container starts in interactive mode: 
```shell
# pytest should be run fro the pytest directory
cd ../test && pytest
```
### Whats happening: 
- pytest auto-discovers files and directories with "test" in the name to create a set of things to be tested. 
- pytest manages setup/teardown of a test postgres database while it sets up and tears down tests. This can be overriden on a system or test by test basis to use in-memory sqllite for more speed if needed. 
- If it becomes relevant to test on "real" data in CI, it's possible to create the test database by restoring a snapshot of prod and then pointing pytest at the restored backup.
