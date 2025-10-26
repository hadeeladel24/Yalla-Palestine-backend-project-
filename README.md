# Yalla Palestine - Tourism Booking API

A comprehensive REST API for tourism booking services in Palestine, built with Flask and integrated with Stripe payment processing.

## Features

- 🔐 **Authentication & Authorization**: JWT-based authentication with role-based access control
- 🏨 **Hotel Management**: Create, search, and manage hotel bookings
- 🍽️ **Restaurant Management**: Book restaurant tables with time slots
- 📍 **Tourist Sites**: Explore and book visits to historical sites
- ✈️ **Trip Planning**: Plan complete trips with hotels, restaurants, and sites
- 💳 **Payment Processing**: Integrated Stripe payment gateway
- ⭐ **Reviews & Ratings**: User reviews for hotels, restaurants, and sites
- 📚 **API Documentation**: Interactive Swagger documentation

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended
- **Payment**: Stripe
- **Documentation**: Flasgger (Swagger)
- **OAuth**: Google OAuth2 integration

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd yalla-palestine-backend
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/palestine_tourism
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLIC_KEY=your-stripe-public-key
CURRENCY=USD
```

5. Run the application
```bash
python app.py
```

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token
- `GET /auth/get_user` - Get current user
- `GET /auth/login/google` - Google OAuth login

### Hotels (`/hotel`)
- `POST /hotel/create_hotel` - Create hotel (owner/admin)
- `GET /hotel/get_all_hotels` - Get all hotels
- `GET /hotel/get_hotel_by_id` - Get hotel by ID
- `GET /hotel/get_hotels_by_location` - Search by location
- `GET /hotel/get_hotels_by_rating_range` - Filter by rating

### Restaurants (`/resturent`)
- `POST /resturent/create_resturent` - Create restaurant (owner/admin)
- `GET /resturent/get_all_resturents` - Get all restaurants
- `GET /resturent/get_resturent_by_id` - Get restaurant by ID

### Tourist Sites (`/sites`)
- `POST /sites/create_site` - Create tourist site (owner/admin)
- `GET /sites/get_sites` - Get all sites
- `GET /sites/get_site_by_id` - Get site by ID

### Bookings (`/booking`)
- `POST /booking/hotel` - Create hotel booking (with Stripe payment)
- `POST /booking/restaurant` - Create restaurant booking (with Stripe payment)
- `POST /booking/<booking_id>/confirm-payment` - Confirm payment

### Trips (`/trips`)
- `POST /trips/create_trip` - Create trip (admin)
- `GET /trips/get_all_trips` - Get all trips

### Reviews (`/reviews`)
- `POST /reviews/create_review` - Create review (user)
- `GET /reviews/get_reviews_by_user_id` - Get user reviews

## API Documentation

Access interactive Swagger documentation at:
```
http://localhost:5000/swagger
```

## Authentication

Most endpoints require JWT authentication. Include the token in the request header:
```
Authorization: Bearer <your-jwt-token>
```

## User Roles

- **user**: Regular users (can book and review)
- **owner**: Business owners (can create hotels/restaurants/sites)
- **admin**: Full system access
- **guest**: Limited access

## Payment Integration

The API uses Stripe for payment processing:
- All bookings create a Stripe Payment Intent
- Client receives `client_secret` for frontend integration
- Payment confirmation updates booking status

## Rate Limiting

Some endpoints are rate-limited for security:
- Login: 3 attempts per minute
- Create operations: 3 per minute

## Database Schema

### Main Models
- **User**: Users, owners, admins
- **hotel**: Hotel listings
- **restaurant**: Restaurant listings
- **torist_place**: Tourist sites
- **booking**: Hotel and restaurant bookings with Stripe integration
- **review**: User reviews
- **trips**: Complete trip packages

## Environment Setup

The application requires PostgreSQL. Update `SQLALCHEMY_DATABASE_URI` in your `.env` file.

## Development

Run in debug mode:
```bash
python app.py
```

The app runs on `http://localhost:5000` by default.

## License

This project is proprietary software for Palestine tourism services.

## Support

For issues or questions, contact the development team.

