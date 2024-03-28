#!/bin/bash

mkdir -p $HOME/.local/bin $HOME/.local/share

cp gallery_5000 $HOME/.local/bin

sudo cp gallery_5000.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gallery_5000.service

