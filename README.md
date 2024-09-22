# Volleyball Match Analysis Dashboard

This project is a **Dash-based web application** that allows you to analyze volleyball match data from a **SQLite** database. It provides visualizations for player performance metrics (efficiency, positivity, total counts) and setter distribution on a volleyball court.

## Features

- **Player Performance Analysis**: Visualize player efficiency, positivity, and counts for skills like Attacco (Attack), Ricezione (Reception), and Battuta (Serve).
- **Setter Distribution**: Visualize the distribution of setter actions on a volleyball court.
- **Interactive Dashboards**: Use dropdowns and tabs to filter data by teams, skills, and setter positions.

## Prerequisites

You need to have **conda** installed. If you don’t have it, download and install [Anaconda](https://www.anaconda.com/products/individual).

## Installation

1. **Clone this repository**:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. **Set up the conda environment** using the provided `environment.yml` file:
    ```bash
    conda env create -f environment.yml
    ```

3. **Activate the environment**:
    ```bash
    conda activate your-environment-name
    ```

4. **Run the app**:
    ```bash
    python app.py
    ```

   The app will start running at `http://127.0.0.1:8050/` by default. You can access it through your web browser.

## Database Setup

The application loads volleyball match data from a **SQLite database**. Ensure that your `.db` file is correctly set up and accessible. Update the path to the database in the script (`db_path` variable) to match your local file system.

The database is expected to contain the following tables:
- `event`: Contains event logs of match activities, such as actions performed by players.
- `player`: Stores player data.
- `team`: Stores team data.

The app queries and processes these tables to generate performance metrics and visualizations.

## Usage

Once the app is running, you can:
- Select a skill (e.g., Attacco, Ricezione, Battuta) from the dropdown menu.
- Select a team to view the performance of players from that team.
- View the top players based on total actions, efficiency, and positivity.
- Switch between tabs to see **Player Performance** or **Setter Distribution**.
  
### Interactive Setter Distribution Visualization:
- In the **Setter Distribution** tab, choose a setter position to see how their sets are distributed across the court.
- The court diagram will show circles indicating the number of sets made to different areas, with larger circles representing more frequent sets.

## Contributing

Feel free to open issues or submit pull requests to improve this project!

