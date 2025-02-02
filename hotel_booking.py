from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Initialize hotel_rooms globally
hotel_rooms = {}

# Step 1: Initialize the hotel structure
def initialize_rooms():
    rooms = {}
    # Floors 1-9: 10 rooms each
    for floor in range(1, 10):
        rooms[floor] = {floor * 100 + i: True for i in range(1, 11)}
    # Floor 10: 7 rooms
    rooms[10] = {1000 + i: True for i in range(1, 8)}
    return rooms

# Step 2: Randomly mark rooms as occupied
def randomize_occupancy(rooms, occupancy_rate=0.3):
    total_rooms = sum(len(floor_rooms) for floor_rooms in rooms.values())
    num_occupied = int(total_rooms * occupancy_rate)

    all_rooms = [(floor, room) for floor, floor_rooms in rooms.items() for room in floor_rooms]
    occupied_rooms = random.sample(all_rooms, num_occupied)

    for floor, room in occupied_rooms:
        rooms[floor][room] = False  # Mark as occupied
        
# Step 3: Booking functionality
def book_rooms(rooms, num_rooms):
    # Enforce the 5-room limit
    if num_rooms > 5:
        print("Cannot book more than 5 rooms at a time.")
        return None  # Return None to indicate invalid booking

    booked_rooms = []

    # Rule 1: Try to book rooms on the same floor
    for floor, floor_rooms in rooms.items():
        available_rooms = [room for room, available in floor_rooms.items() if available]
        if len(available_rooms) >= num_rooms:
            booked_rooms = available_rooms[:num_rooms]
            for room in booked_rooms:
                rooms[floor][room] = False  # Mark as occupied
            return booked_rooms

    # Rule 2: Book across multiple floors, minimizing travel time
    all_available_rooms = [
        (floor, room)
        for floor, floor_rooms in rooms.items()
        for room, available in floor_rooms.items()
        if available
    ]

    if len(all_available_rooms) >= num_rooms:
        # Sort rooms by floor and room number to minimize travel
        all_available_rooms.sort(key=lambda x: (x[0], x[1]))
        booked_rooms = all_available_rooms[:num_rooms]
        for floor, room in booked_rooms:
            rooms[floor][room] = False  # Mark as occupied
        return [room for _, room in booked_rooms]

    # If not enough rooms are available
    print("Not enough rooms available to fulfill the booking request.")
    return None


# Step 4: Visualize the room status
def visualize_rooms(rooms, booked_rooms=None):
    floor_visuals = []
    for floor, floor_rooms in sorted(rooms.items()):
        floor_visual = []
        for room, status in floor_rooms.items():
            if booked_rooms and room in booked_rooms:
                floor_visual.append("🟡")  # Booked
            elif status:
                floor_visual.append("🟢")  # Available
            else:
                floor_visual.append("🔴")  # Occupied
        floor_visuals.append(f"Floor {floor}: {' '.join(floor_visual)}")
    return "\n".join(floor_visuals)

# Routes
@app.route("/")
def home():
    # Ensure hotel_rooms is initialized before accessing the home route
    global hotel_rooms  # Ensure we use the global hotel_rooms variable
    return render_template("home.html", rooms=hotel_rooms)

@app.route("/randomize")
def randomize():
    global hotel_rooms
    randomize_occupancy(hotel_rooms)
    return redirect(url_for("home"))

@app.route("/reset")
def reset():
    global hotel_rooms
    hotel_rooms = initialize_rooms()  # Reinitialize the rooms
    return redirect(url_for("home"))

@app.route("/book", methods=["POST"])
def book():
    num_rooms = int(request.form.get("num_rooms", 0))

    if num_rooms > 5:  # Enforce the limit here
        message = "You can only book up to 5 rooms at a time."
        return render_template("home.html", rooms=hotel_rooms, message=message)

    booked = book_rooms(hotel_rooms, num_rooms)
    if not booked:
        message = "No rooms available to fulfill the booking request."
    else:
        message = None
    return render_template("home.html", rooms=hotel_rooms, booked=booked, message=message)


if __name__ == "__main__":
    # Initialize rooms once when the app starts
    hotel_rooms = initialize_rooms()
    app.run(debug=True)
