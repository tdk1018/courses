#!/bin/bash
# Assignment 2, Exercise 2: Greetings
#
# Using the variables below, print:
#   Hello
#   [first_name][TAB][last_name]
#   How are you?
#
# The tab must be an actual tab character, not spaces.
# Hint: How does echo handle special characters like \t?

first_name=Jane
last_name=Doe

# Do not modify the above. Start your code here.

echo -e "Hello 
$first_name\t$last_name
How are you?"