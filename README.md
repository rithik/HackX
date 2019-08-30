# HackX

### Why use this system?

There are so many different systems that provide the ability to register people for events, but there is no one system that covers all of the things required for running a hackathon. This is where HackX comes in. HackX is the first system that involves hacker registration, mentor registration, judge registration, mentor-ticket queueing, administration views with data analysis, a resume book and judging. We know that's a lot for one system to do. Here's some instructions for setup. The judging application is currently held in a different repository [https://github.com/hackersatuva/judging](https://github.com/hackersatuva/judging). Eventually, these two repositories will be merged into one repository.

### Localhost setup

1. Clone this repository: `git clone https://github.com/rithik/HackX`
2. Rename the `secret.py.example` file to the `secret.py`. Use `cp secret.py.example secret.py` or `mv secret.py.example secret.py`. Add in appropriate variables. Make sure to change the `SECRET_KEY` field.  
3. [Setup the Database](#setting-up-the-database)
4. Clone the judging repository: `git clone https://github.com/hackersatuva/judging`
5. Start the docker container by running: `docker-compose up`
6. In the `settings.py` file, make sure to change the JUDGING_URL value. For localhost development, the value should be `http://localhost:5082`
7. Run the flask server by running `./run.sh dev`.
8. Navigate to `http://localhost:5000` and you should see a login screen. You have now setup the HackX environment.

### Setting up the Database

First, install PostgreSQL by going to [https://www.postgresql.org/download/](https://www.postgresql.org/download/). 

Once PostgreSQL is installed, create a new database. You can do this by running `psql`. This will open up a new shell to access the database. Next, create the database by running `CREATE DATABASE DATABASE_NAME;`, replacing `DATABASE_NAME` with your database name. Exit the shell by typing `\q`. 

Change the DB_URL value in your `secret.py` file to use the following format: `postgresql://localhost/DATABASE_NAME`. 

When you are using a cloud based database (such as Google Cloud or AWS), use the following connection string: `postgresql://USERNAME:PASSWORD@IP_ADDRESS/DATABASE_NAME`.

### Things to know

Make sure that your Gmail account is allowed to send emails from less secure apps. Follow directions here: [https://support.google.com/accounts/answer/6010255?hl=en](https://support.google.com/accounts/answer/6010255?hl=en)

To setup a user as an admin in the HackX system, navigate to `http://localhost:5000/make/admin`. Use the `ADMIN_PASSWORD` set in the `secret.py` file.

To setup a user as an mentor in the HackX system, navigate to `http://localhost:5000/make/mentor`. Use the `MENTOR_PASSWORD` set in the `secret.py` file.

To setup a user as a judge in the HackX system, navigate to `http://localhost:5000/make/judge`. Use the `JUDGE_PASSWORD` set in the `secret.py` file.
