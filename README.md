## To run the project locally
- Start redis
  ```bash
  docker run --rm -p 6379:6379 redis:7
  ```
- Run development server
  ```bash
  python manage.py runserver
  ```
## To run end-to-end tests 
- Install [Google Chrome](https://www.google.com/chrome/).
- Install [Chrome Driver]((https://googlechromelabs.github.io/chrome-for-testing/) ) for the same version as above.
- Install selenium `pip install selenium`