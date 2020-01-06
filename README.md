# The Sweat Notebooks

*The Sweat Notebooks* is an application that gives you reports about your Strava activities. The reports are generated from parametrized Jupyter notebooks.

I developed this application as a side project because I wanted to try to combine a few technologies:

- [Papermill](https://papermill.readthedocs.io/en/latest/) to parametrize and execute Jupyter Notebook templates.
- [Nbconvert](https://nbconvert.readthedocs.io/en/latest/) to convert the generated Jupyter Notebooks into html.
- [Strava webhooks](https://developers.strava.com/docs/webhooks/) to get a webhook trigger from Strava when you upload a new activity.

The rest of the technology stack is:
- [FastAPI](https://fastapi.tiangolo.com/), a Python web framework.
- [Docker](https://www.docker.com/)
- [Dokku](http://dokku.viewdocs.io/dokku/), a Heroku alternative that is running on my personal server.

The design (yes, calling it design might be a stretch) may look very basic.
That has a few reasons:
1. I am lazy.
2. I am not a frontend developer and definitely not a designer.
3. I do not want you to get distracted by a fancy user interace.
4. I like [brutalist web design](https://brutalist-web.design/).

## Getting started
Run the application with this command: TODO
Then head over to the login page and connect with Strava. Then when you upload a new activity to Strava, your reports will be added to the reports page.

## Development
This application is still in development. Some features I will likely add in the future:
- Generating report for activities that were uploaded before a user connected this application to Strava.
- Support for multiple reports and reports for different types of activities.
- Allow uploading custom Jupyter Notebook templates.
- Track features that are computed in the notebook over time by using [Scrapbook](https://nteract-scrapbook.readthedocs.io/) (another tool that I would like to try).
