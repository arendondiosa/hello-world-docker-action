#!/bin/sh -l

number_of_commits=$(git rev-list --count HEAD ^$1)
echo "Number of commits: $number_of_commits"

darker --diff -r HEAD~$number_of_commits .
