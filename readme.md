# Instructions:
The commands to prepare the environment and start the frontend and backend servers is given below. (First `cd` into to the project directory)

### Backend:
Run the development server using the following commands in separate terminals in the same order:
```
cd backend
. ./flask_server_start.sh
. ./redis_start.sh
. ./mailhog_start.sh
. ./workers_start.sh
. ./beat_start.sh
```

### Frontend:
Run the development server using the following command:
```
cd frontend
npm install
vue serve
```
