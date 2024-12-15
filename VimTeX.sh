#!/bin/bash

# This script installs VimTeX for Vim and sets up a LaTeX-friendly environment

# Ensure the system is updated
echo "Updating system package list..."
sudo apt update -y    # For Ubuntu/Debian-based systems, adjust for your distro if needed

# Step 1: Install necessary dependencies
echo "Installing dependencies..."
sudo apt install -y \
        vim \
            curl \
                git \
                    build-essential \
                        texlive \
                            texlive-latex-extra \
                                texlive-fonts-recommended \
                                    latexmk

# Step 2: Install a LaTeX distribution (if texlive isn't already installed)
# Uncomment the following line if texlive isn't installed or if you need a specific package
# sudo apt install -y texlive-full

# Step 3: Install Vim-Plug (Vim Plugin Manager)
echo "Installing Vim-Plug plugin manager..."

# Create autoload directory if it doesn't exist
mkdir -p ~/.vim/autoload ~/.vim/plugged

# Download vim-plug (plugin manager) if it's not already installed
if [ ! -f ~/.vim/autoload/plug.vim ]; then
        curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
                    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
            echo "vim-plug installed."
        else
                echo "vim-plug is already installed."
fi

# Step 4: Configure Vim to use VimTeX
echo "Configuring Vim for VimTeX..."

# Check if .vimrc exists, if not create it
if [ ! -f ~/.vimrc ]; then
        echo "Creating .vimrc file..."
            touch ~/.vimrc
fi

# Add VimTeX plugin to the .vimrc file
echo "Adding VimTeX plugin configuration to .vimrc..."
cat <<EOL >> ~/.vimrc

" VimTeX Configuration
call plug#begin('~/.vim/plugged')

" VimTeX plugin
Plug 'lervag/vimtex'

call plug#end()

" Enable line numbering
set number

" Enable syntax highlighting
syntax enable

" Enable auto-indentation for LaTeX
filetype plugin indent on

EOL

# Step 5: Install the plugin via vim-plug
echo "Installing VimTeX plugin..."
vim +PlugInstall +qall

# Step 6: Verify VimTeX installation
echo "Verifying VimTeX installation..."
vim -c 'helptags ~/.vim/plugged/vimtex/doc' -c 'q'

# Step 7: Install additional LaTeX packages (optional)
# Optional: Add any other LaTeX packages or fonts you might need
# echo "Installing additional LaTeX packages..."
# sudo apt install -y texlive-science texlive-lang-german texlive-pictures

echo "VimTeX installation complete! You can now use Vim with LaTeX support."


