# Rewritten - Next.js Frontend

This is the Next.js frontend for the Rewritten application, an interactive historical narrative experience.

## Architecture Overview

This project uses a hybrid architecture:
- **Flask Backend**: Handles AI video generation, database operations, and narrative generation
- **Next.js Frontend**: Provides a modern UI and improved user experience

## Setup

1. Ensure you have the Flask backend set up and ready to run:
   - Flask dependencies installed (`pip install -r requirements.txt`)
   - Database initialized
   - Environment variables configured

2. Install Next.js dependencies:
   ```
   npm install
   ```

3. Configure environment variables:
   - Create a `.env.local` file with:
   ```
   NEXT_PUBLIC_FLASK_API_URL=http://localhost:5000
   ```

## Running the Application

### Development Mode

To run both the Flask backend and Next.js frontend simultaneously:

```
npm run dev:all
```

This will start:
- Flask backend on http://localhost:5000
- Next.js frontend on http://localhost:3000

### Run Separately

To run the Next.js frontend only:

```
npm run dev
```

To run the Flask backend only:

```
npm run flask
```

## Building for Production

1. Build the Next.js application:
   ```
   npm run build
   ```

2. Start the production Next.js server:
   ```
   npm run start
   ```

3. Run the Flask server separately in production mode.

## Project Structure

- `src/app`: Next.js app router pages
- `src/components`: React components
- `src/lib`: Utility functions and API communications

## API Communication

The frontend communicates with the Flask backend for:
- Retrieving scenarios
- Starting new game sessions
- Processing player decisions
- Getting video content

The Flask backend handles all AI-related operations and database interactions.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
