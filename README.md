# 5CCS2SEG_Major_Group_Project: :book: Book Club :book:
![picture alt](https://img.shields.io/badge/tests-607%20passed-brightgreen)
![picture alt](https://img.shields.io/badge/coverage-93%25-green)
![picture alt](https://img.shields.io/badge/licence-MIT-9cf)
=============
This is a readme file for our SEG Major Group Project.

## Table of Contents
  * [Contributors](#Contributors "Go to Contributors")
  * [Description](#Description "Go to Description")
  * [Features](#Features "Go to Features")
  * [Technologies](#Technologies "Go to Technologies")
  * [Installations](#How-to-run-the-project "Go to Installations")
  * [License](#License "Go to License")
  * [Reference List](#Reference-list "Go to Reference List")

## Contributors
**Team Name: Major Group**
:space_invader:***Artificial Intelligence Group:***
  * Rishi Ganeshan (K20004392)
  * Encheng Wu (K20070867)
  * Yanjing Xia (K20013191)

:computer:***Software Development Group:***
* An Hsu (K20002093)
* Grace Edgecombe (K20006917)
* Xuechao Yan (K19006213)
* Encheng Wu (K20070867)
* Zena Wang (K20041870)
* Zirui Ding (K20044217)
* Anqi Jin (K20073503)

## Description
**Book Club** is a club management web application where the user can explore and join book clubs in order to discuss books according to their preferences. This is a social networking platform where bookworms can share their thoughts about books they have read in their own time and for meetings (in person or online) or simply via creating a post in one of the clubs that they belong to. Our AI system will also recommend users books that club members might like when they create a meeting (the preferences of the club members will affect the recommendations of the system).

## Features
* When the user has signed up and logged into the website they will be redirected to the club home page where:
	* A different book quote will be displayed everyday
	* Advantages of reading will be displayed in order to encourage people to read books
* All users can:
	* Create a profile and edit it afterwards
	* Create, join and leave book clubs
	* Explore different clubs according to their preferences
	* Create an application to join private clubs (users are automatically accepted to public clubs)
	* Explore and rate books in the book list section, and filter them by genre
	* Add books to their reading list where they can set their reading status as: unread, reading and finished reading
* As a club member, you can:
  * See a list of all the people in the club
  * Create meetings that others can join on the day using Zoom if it is an online-based club
  * Join meetings that have been hosted by others in the club
  * Create posts that are put on the club feed
  * Comment and upvote or downvote posts to express opinions on other people's posts
  * Delete their own posts
* As a club moderator, you can:
  * Do all the things that a member can do
  * Accept and reject applications to the club
  * Remove members who are being disruptive
* As a club owner, you can:
  * Do all the things that a moderator can
  * Modify the club's information
  * Transfer the ownership of the club to a moderator
  * Promote a member to moderator
  * Demote a moderator to member
  * Ban a member from the club, so the member can no longer access the club and cannot re-apply for the club
  * Delete the club
* An interactive dinosaur game will be displayed while the system loads the book recommendations

## Technologies
* Our project was built employing Python/Django.
* **Keras**, **TensorFlow**, **Numpy** and **Pandas** were used to produce the (AI) Recommender system
* **Libgravatar** was used to show the users’ profile pictures
* **Coverage** was used for monitoring the program’s testing
* **Faker** was used to generate fake data for seeding the database
* **Google-pasta** was used to generate hidden game
* **Bootstrap** was used to design the program's front-end

<!-- The location where the software or software component is deployed and sufficient information to access it.  The latter includes access credentials for the different types of user who may employ the software. -->
## Deployment
The location where the software is deployed is **Heroku**.
Test club = Test club 1(online and private)
Owner:
*Username = @Owner
*Password = Password123
Moderator:
*Username = @Moderator
*Password = Password123
Member:
*Username = @Member
*Password = Password123
Banned member:
*Username = @BannedMember
*Password = Password123
Meeting host is @Owner
Meeting attendee is @Member
Post comments applications and ratings are randomly created

## How to run the project
Book Clubs - Django Web Application Setup Instructions  

**1. Install virtual environment:**  

    virtualenv venv  

**2. Launch virtual environment:**  

    source venv/bin/activate  

**3. Install required applications:**  

    pip3 install -r requirements.txt  

**4. Get the database:**  

    python3 manage.py makemigrations
    python3 manage.py migrate  

**5. Create Super User:**  

    python3 manage.py createsuperuser  

**6. Seeder and unseeder (Seeder can only be run once, unless run unseed again):**  

    python3 manage.py seed
    python3 manage.py unseed  

**7. Run the server/application:**  

    python3 manage.py runserver  

**8. Run the tests:**  
  *-If the program gives test errors run first:*  

    python3 manage.py collectstatic  
  *then*  

    python3 manage.py test  
  *-If you want to test with coverage:*    

    coverage run manage.py test

    coverage report --omit="*/tests/*"

    coverage html --omit="*/tests/*"



## License
By contributing, you agree that your contributions will be licensed under its *MIT License*.

## Reference List
* The hidden game was adapted from [Dino-Game](https://github.com/WebDevSimplified/chrome-dino-game-clone "Dino-Game") :video_game:
