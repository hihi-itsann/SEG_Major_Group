# 5CCS2SEG_Major_Group_Project: Book Club
This is a readme file for our SEG Major Group Project.
## Table of Contents
  *[Contributors](#Contributors "Goto Contributors")

## Contributors
***Artificial Intelligence Group:***
  * Rishi Ganeshan (K20004392)
  * Encheng Wu (K20070867)
  * Yanjing Xia (K20013191)

***Software Development Group:***
* An Hsu (K20002093)
* Grace Edgecombe (K20006917)
* Xuechao Yan (K19006213)
* Encheng Wu (K20070867)
* Zena Wang (K20041870)
* Zirui Ding (K20044217)
* Anqi Jin (K20073503)

## Description
**Book Club** is a book clubs management web application where the user can explore and join book clubs in order to discuss about books according to their preferences. This is a networking platform where bookworms can share their thoughts about books they have read during meetings (either in person or online) or simply via creating a post in the clubs they belong to. Our AI system will also recommend users books according to the clubs they have joined (the preferences of the club members will affect the recommendations of the system).

## Features
* When the user has signed up and logged into the website they will be redirected to the club home page where:
	* A different book quote will be displayed everyday
	* Profits of reading will be displayed in order to encourage people to read books
* All users can:
	* Create a profile and edit it afterwards
	* Create, join and leave book clubs
	* Explore different clubs according to their preferences
	* Create an application to join private clubs (users are automatically accepted to public clubs)
	* Join meetings that can be either online or in person
	* Create posts on the club feed
	* Upvote/downvote, comment on posts
	* Delete own posts
	* Explore and rate books in the book list section, and filter them by genre
	* Add books to their reading list where they can set their reading status as: unread, reading and finished reading.
* As a club moderator or owner you can:
	** Create meetings that can be either online or in person
  * See club applicants, members and banned members
* As a club owner you can:
	* Modify club info and delete the club
* An interactive dinosaur game will be displayed while the system loads the book recommendations

## Technologies
* Our project was built employing Python/Django.
* Keras, TensorFlow, Numpy and Pandas were used to produce the (AI) Recommender system
* Libgravatar was used to provide url to users’ profile picture
* Coverage was used for monitoring the programme’s testing
* Faker was used to generate fake data for bootstrapping the database
* Google-pasta was used to generate hidden game
* Bootstrap

## How to run the project
Book Clubs - Django Web Application Setup Instructions
1. Install virtual environment:
virtualenv venv
2. Launch virtual environment:
source venv/bin/activate
3. Install required applications:
pip3 install -r requirements.txt
4. Get the database
python3 manage.py makemigrations
python3 manage.py migrate
5. Create Super User:
python3 manage.py createsuperuser
6. Seeder and unseeder (Seeder can only be run once, unless run unseed again):
python3 manage.py seed
python3 manage.py unseed
7. Run the server/application:
python3 manage.py runserver
8. Run the tests:
python3 manage.py test

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## Reference List
* The hidden game was adapted from [Dino-game](https://github.com/WebDevSimplified/chrome-dino-game-clone "Dino-Game")
