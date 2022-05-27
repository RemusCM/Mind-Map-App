# Mind-Map-App

Mind-Map-App is a basic web service with a few endpoints, and can be used to make different requests to the users, mindmaps, and leafs APIs. This web service has over 90% code coverage, and can be easily used with docker.

## Requirements
Docker/Docker-compose

## Usage

After cloning the repository: In a terminal at the location of the project, run the following:

```bash
docker-compose up --build --remove-orphans

```

This will take a few minutes to build and run the server on port 8000. Once it's built,
go to http://localhost:8000/api/docs to see all possible endpoints. Otherwise, here is an example scenario that you can run.

###### Creating a User
```bash
curl -X POST "http://localhost:8000/api/user/create/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"email\":\"test1@example.com\",\"password\":\"testpassword123\",\"name\":\"John Doe\"}"
```

###### Retrieving User Token to be used as authentication
```bash
curl -X POST "http://localhost:8000/api/user/token/" -H  "accept: application/json" -H  "Content-Type: application/x-www-form-urlencoded" -d "email=test1%40example.com&password=testpassword123"
```

Copy the token you receive. In my example, I have the response:
```bash
{"token":"06c17435cf79667fae4ddecf8662b8757c14e0a7"} 
```
We can now use this token as a header in our cURL commands. In future commands, replace <ACCESS_TOKEN> with your token. 

###### Creating a MindMap. 

```bash
curl -X POST "http://localhost:8000/api/mindmap/mindmaps/" -H  "accept: application/json" -H  "Content-Type: application/json" -H  "Authorization: Token <ACCESS_TOKEN>" -d "{\"title\":\"Sample MindMap\"}"
```

Keep in mind the id of the map you create. If it's the first one, the id will be 1.

###### Creating multiple leafs

```bash
curl -X POST "http://localhost:8000/api/mindmap/leafs/" -H  "accept: application/json" -H  "Content-Type: application/json" -H  "Authorization: Token <ACCESS_TOKEN>" -d "{\"mindmap\":1,\"path\":\"i/like/potatoes\",\"text\":\"Because reasons\"}"


curl -X POST "http://localhost:8000/api/mindmap/leafs/" -H  "accept: application/json" -H  "Content-Type: application/json" -H  "Authorization: Token <ACCESS_TOKEN>" -d "{\"mindmap\":1,\"path\":\"i/eat/tomatoes\",\"text\":\"Because other reasons\"}"
```

###### Retrieving a Specific leaf

For this requirement, we are just feeding the id of the leaf, and nothing related to the mindmap. 
I thought it'd be redundant to need the id of the mindmap as we'd still need to use the leaf id, which is also a primary key. 

```bash
curl -X GET "http://localhost:8000/api/mindmap/leafs/1/" -H  "accept: application/json" -H  "Authorization: Token <ACCESS_TOKEN>"
```

which outputs:
```bash
{
  "id": 7,
  "path": "i/like/potatoes",
  "text": "Because reasons"
}
```

###### Pretty Printing a whole mindmap
```bash
curl -X GET "http://localhost:8000/api/mindmap/mindmaps/1/" -H  "accept: application/json" -H  "Authorization: Token <ACCESS_TOKEN>"
```

which outputs:
```bash
Sample Mindmap/
	i/
		like/
			potatoes
		eat/
			tomatoes
```
## Testing and Linting
Locally, you can run these two commands. For linting, run
```bash
docker-compose run --rm app -sh -c "flake8"
```


For testing with code coverage, run

```bash
docker-compose run --rm app sh -c "coverage run manage.py test && coverage report"
```

Otherwise, you can also run the Test and Lint workflow on the Actions tab. 

## Points to improve
Remove unnecessary branches.
Add deployment to cloud. I tried in another branch (implementDeployment), but it was taking too long, and it was my first time trying, and I was running into issues. 

