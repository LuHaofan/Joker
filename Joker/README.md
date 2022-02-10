# How to use
1. Install Django 4.0.1 on your local machine
2. Clone this repo to your local machine
3. In the current directory (same as `manage.py`), start a terminal and enter command: `python manage.py runserver`. Make sure your default python version is Python3, otherwise you need to specify it explicitly: `python3 manage.py runserver`
4. In your browser, enter the following URL: [http://127.0.0.1:8000/editor/]
5. You should be able to see the full example here.

# How to modify
1. Go to [./editor/templates/index.html](./editor/templates/index.html) This is the template file for full example.

# Save and load
- Find the `note-list.json` file in the `./editor/static/editor/json/` folder. It is an example of how my server side code will generate the format of json file.
- In the `index.html` page, create a sidebar (you can adjust the width of the editor, if it looks better), display the notes' title as a list, give the title a `<a href="path"> </a>` tag, where the `path` is the value of `path` property in json file.

# Setting up Neo4j (Local Development for Testing)
Requirements:
`pip install neomodel django-neomodel`

If running Python 3.10, may need to use a virtual environment running Python 3.9 because some parts of neo4j are incompatible with Python 3.10

1. Install Neo4j Desktop from here https://neo4j.com/try-neo4j/
2. Create a new DBMS in Neo4j Desktop, user="neo4j" password="12345"
3. Start the DBMS
4. Run `python manage.py install_labels`
5. Run `python init_test_data.py` script to create some example nodes

# Phase 2 functions
1. click `New` button to create a new note, the default name for the new note is `new note.md`.
2. click `Export` to download the note to local
3. click `Save` to save the note to server
4. click `Preview` to see the preview of the markdown note
5. click `choose file` to import a note from local machine
6. You can rename the note at the textbox
7. You can find all the notes in the `Note list` sidebar.


# Phase 3 JSON Example
- Please see [here](./editor/static/editor/json/note-list.json) for an example JSON file
- @Owen, use this JSON file to generate the subtitle and info window for the note.
- @Daisy, please try to fit it in you database framework. Let me know if there is any problem.