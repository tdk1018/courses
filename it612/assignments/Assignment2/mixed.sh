#!/bin/bash
# Assignment 2, Exercise 3: Mixed Messages
#
# Print "Everything is fine" to stdout
# Print "WARNING: SEVERE ERROR" to stderr
#
# Both will appear on screen when you run the script,
# but they should travel through different streams.
# Hint: How do you redirect output to a specific file descriptor?

# Your code here

echo "Everything is fine"
echo "WARNING: SEVERE ERROR" >&2