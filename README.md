# clippings

[![Build Status](https://github.com/yakimka/clippings/actions/workflows/workflow-ci.yml/badge.svg?branch=main&event=push)](https://github.com/yakimka/clippings/actions/workflows/workflow-ci.yml)
[![Codecov](https://codecov.io/gh/yakimka/clippings/branch/main/graph/badge.svg)](https://codecov.io/gh/yakimka/clippings)

**Clippings** is a web application designed to help avid readers and researchers manage and preserve
their book highlights and notes, particularly those from Kindle devices. It offers a centralized
platform to import, organize, review, and export your valuable insights gleaned from reading.

## Overview

Have you ever highlighted a brilliant passage in a book, only to forget it later or struggle to find
it when you need it most? Clippings solves this problem by providing a user-friendly interface to
manage your digital reading annotations. Instead of your highlights being locked away on a single
device or lost in a proprietary format, Clippings empowers you to own, access, and utilize your
reading data effectively.

This project aims to:

- **Preserve Your Insights:** Store and back up your Kindle clippings.
- **Enhance Discoverability:** Easily browse and revisit your highlights and notes.
- **Facilitate Knowledge Management:** Organize your reading material, add reviews, ratings, and
  inline notes to your clippings.
- **Promote Data Portability:** Export your data in an open format, ensuring you always have control
  over your information.

![Books List Screenshot](/screenshots/books_list.png)

## Key Features

- **Kindle Clippings Import:** Seamlessly import your "My Clippings.txt" file from your Kindle
  device. The application intelligently parses and organizes clippings by book and author.
- **Book Management:**
    - View all imported books with details like title, author, and cover art (fetched from Google
      Books API).
    - Add or edit book reviews and ratings.
    - Edit book title and author information.
- **Clipping Organization:**
    - Browse clippings grouped by book.
    - View individual clipping details including page number, location, and date added.
    - Edit the content of existing clippings.
- **Inline Notes:** Add personal notes directly to your highlights, enriching your understanding and
  recall. These notes can be edited or unlinked.
- **Data Export & Backup:** Export all your books, clippings, and notes in a structured JSON
  format (NDJSON), allowing for easy backup or migration.
- **Data Restoration:** Restore your library from a previously exported backup file.
- **Intelligent Note Linking:** Automatically links notes made on Kindle to their corresponding
  highlights.
- **Deleted Item Memory:** Remembers deleted books and clippings to prevent accidental re-import,
  with an option to clear this memory.
- **Responsive Design:** Access your clippings on various devices thanks to a clean, responsive
  interface built with Pico.css.

![Books Page Screenshot](/screenshots/book.png)

## Who is this for?

Clippings is ideal for:

- **Students and Researchers:** Who need to organize and revisit key information from their academic
  reading.
- **Avid Readers:** Who want to preserve memorable quotes and passages from their favorite books.
- **Writers and Content Creators:** Who draw inspiration and references from their reading material.
- **Anyone who uses a Kindle:** And wishes for a more robust and open way to manage their highlights
  and notes.

By providing a dedicated and organized space for your book clippings, this project helps you turn
passive reading into an active and reusable knowledge base.

## Development

### Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Copy the example settings file and configure your settings:
   ```bash
   cp settings.example.yaml settings.yaml
   ```
3. Build the Docker images:
   ```bash
   docker-compose build
   ```
4. Start the service:
   ```bash
   docker-compose up
   ```

### Making Changes

1. List available `make` commands:
   ```bash
   make help
   ```
2. Check code style with:
   ```bash
   make lint
   ```
3. Run tests using:
   ```bash
   make test
   ```
4. Manage dependencies via Poetry:
   ```bash
   make poetry args="<poetry-args>"
   ```
   - For example: `make poetry args="add requests"`

5. For local CI debugging:
   ```bash
   make run-ci
   ```

#### Pre-commit Hooks

We use [pre-commit](https://pre-commit.com/) for linting and formatting:
- It runs inside a Docker container by default.
- Optionally, set up hooks locally:
  ```bash
  pre-commit install
  ```

#### Mypy

We use [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking.

It is configured for strictly typed code, so you may need to add type hints to your code.
But don't be very strict, sometimes it's better to use `Any` type.

## Available CLI Commands

Project CLI commands are available in the `clippings.cli` module.
List of available commands you can see if you run `python -m clippings.cli --help` command.

## License

[MIT](https://github.com/yakimka/clippings/blob/main/LICENSE)

## Credits

This project was generated with [
`yakimka/cookiecutter-pyproject`](https://github.com/yakimka/cookiecutter-pyproject).
