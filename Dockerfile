# Use an official Python runtime as a parent image
FROM python:3.10

# Set the environment variable for the application home
ENV APP_HOME /app


# Expose port 5666 for the application
EXPOSE 5666

# Set the working directory inside the container
WORKDIR $APP_HOME

# Copy the current directory contents into the container at /app
COPY . $APP_HOME

# Update package lists, install dependencies for Google Chrome and Python
RUN apt-get update && apt-get install -y \
    wget \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libu2f-udev \
    libvulkan1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run app.py when the container launches
ENTRYPOINT ["python", "app.py"]
