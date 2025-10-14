# Copyright (C) 2019, Nokia

*** Settings ***

Library   CreateThread.py

*** Test Cases ***


Create Threads In Loop
   CreateThread.Create Threads In Loop   ${iterations}
