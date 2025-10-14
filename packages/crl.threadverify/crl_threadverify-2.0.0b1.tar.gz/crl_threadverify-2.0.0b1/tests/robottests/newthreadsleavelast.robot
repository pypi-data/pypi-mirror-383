# Copyright (C) 2019, Nokia

*** Settings ***

Library   CreateThread.py

*** Test Cases ***


New Threads Leave Last
   CreateThread.Create Threads And Leave Last    ${numberofthreads}
