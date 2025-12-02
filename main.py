#!/usr/bin/env python3
"""
File Management Automation Tool
Cross-platform file organizer with bulk renaming, sorting, and duplicate detection
"""

import os
import shutil
import hashlib
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

class FileManager:
    def __init__(self):
        self.report = []
        self.file_categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.java', '.cpp', '.c', '.js', '.html', '.css', '.php', '.rb', '.go'],
            'Executables': ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm'],
            'Others': []
        }
    
    def clear_report(self):
        """Clear the current report"""
        self.report = []
    
    def add_to_report(self, message):
        """Add a message to the report"""
        self.report.append(message)
        print(message)
    
    def print_report(self):
        """Print the full operation report"""
        print("\n" + "="*60)
        print("OPERATION REPORT")
        print("="*60)
        for line in self.report:
            print(line)
        print("="*60 + "\n")
    
    def get_file_hash(self, filepath, block_size=65536):
        """Calculate MD5 hash of a file"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(block_size)
                    if not data:
                        break
                    hasher.update(data)
            return hasher.hexdigest()
        except Exception as e:
            print(f"Error hashing {filepath}: {e}")
            return None
    
    def bulk_rename(self, directory, pattern, replacement, use_regex=False):
        """
        Bulk rename files in a directory
        
        Args:
            directory: Path to directory
            pattern: Pattern to search for
            replacement: Replacement string
            use_regex: Use regex pattern matching
        """
        self.clear_report()
        self.add_to_report(f"Starting bulk rename operation in: {directory}")
        self.add_to_report(f"Pattern: '{pattern}' -> Replacement: '{replacement}'")
        self.add_to_report(f"Regex mode: {use_regex}\n")
        
        path = Path(directory)
        if not path.exists():
            self.add_to_report(f"Error: Directory '{directory}' does not exist!")
            return
        
        renamed_count = 0
        error_count = 0
        
        try:
            for item in path.iterdir():
                if item.is_file():
                    old_name = item.name
                    
                    if use_regex:
                        new_name = re.sub(pattern, replacement, old_name)
                    else:
                        new_name = old_name.replace(pattern, replacement)
                    
                    if new_name != old_name:
                        new_path = item.parent / new_name
                        
                        if new_path.exists():
                            self.add_to_report(f"⚠ Skipped '{old_name}': Target name already exists")
                            error_count += 1
                            continue
                        
                        try:
                            item.rename(new_path)
                            self.add_to_report(f"✓ Renamed: '{old_name}' -> '{new_name}'")
                            renamed_count += 1
                        except Exception as e:
                            self.add_to_report(f"✗ Error renaming '{old_name}': {e}")
                            error_count += 1
        
        except Exception as e:
            self.add_to_report(f"Error during bulk rename: {e}")
        
        self.add_to_report(f"\nSummary: {renamed_count} files renamed, {error_count} errors")
        self.print_report()
    
    def sort_files(self, source_directory, create_subdirs=True):
        """
        Sort files into categorized folders based on file type
        
        Args:
            source_directory: Path to directory to organize
            create_subdirs: Create category subdirectories
        """
        self.clear_report()
        self.add_to_report(f"Starting file sorting operation in: {source_directory}\n")
        
        path = Path(source_directory)
        if not path.exists():
            self.add_to_report(f"Error: Directory '{source_directory}' does not exist!")
            return
        
        moved_files = defaultdict(int)
        error_count = 0
        
        try:
            for item in path.iterdir():
                if item.is_file():
                    ext = item.suffix.lower()
                    category = 'Others'
                    
                    # Determine category
                    for cat, extensions in self.file_categories.items():
                        if ext in extensions:
                            category = cat
                            break
                    
                    # Create category folder if needed
                    if create_subdirs:
                        category_path = path / category
                        category_path.mkdir(exist_ok=True)
                    else:
                        category_path = path
                    
                    # Move file
                    destination = category_path / item.name
                    
                    # Handle name conflicts
                    if destination.exists() and destination != item:
                        name_stem = item.stem
                        counter = 1
                        while destination.exists():
                            new_name = f"{name_stem}_{counter}{ext}"
                            destination = category_path / new_name
                            counter += 1
                    
                    try:
                        if destination != item:  # Only move if not already in place
                            shutil.move(str(item), str(destination))
                            self.add_to_report(f"✓ Moved '{item.name}' to {category}/")
                            moved_files[category] += 1
                    except Exception as e:
                        self.add_to_report(f"✗ Error moving '{item.name}': {e}")
                        error_count += 1
        
        except Exception as e:
            self.add_to_report(f"Error during file sorting: {e}")
        
        self.add_to_report("\nCategory Summary:")
        total_moved = 0
        for category, count in sorted(moved_files.items()):
            self.add_to_report(f"  {category}: {count} files")
            total_moved += count
        
        self.add_to_report(f"\nTotal: {total_moved} files organized, {error_count} errors")
        self.print_report()
    
    def find_duplicates(self, directory, remove_duplicates=False):
        """
        Find and optionally remove duplicate files using hash comparison
        
        Args:
            directory: Path to directory to scan
            remove_duplicates: If True, remove duplicate files
        """
        self.clear_report()
        self.add_to_report(f"Scanning for duplicates in: {directory}")
        self.add_to_report(f"Remove duplicates: {remove_duplicates}\n")
        
        path = Path(directory)
        if not path.exists():
            self.add_to_report(f"Error: Directory '{directory}' does not exist!")
            return
        
        # Dictionary to store hash -> list of file paths
        hash_map = defaultdict(list)
        scanned_count = 0
        
        # Scan all files recursively
        self.add_to_report("Calculating file hashes...")
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    file_hash = self.get_file_hash(item)
                    if file_hash:
                        hash_map[file_hash].append(item)
                        scanned_count += 1
                        if scanned_count % 50 == 0:
                            print(f"  Scanned {scanned_count} files...", end='\r')
        
        except Exception as e:
            self.add_to_report(f"Error during scanning: {e}")
        
        print()  # New line after progress
        self.add_to_report(f"Scanned {scanned_count} files\n")
        
        # Find duplicates
        duplicates_found = []
        for file_hash, files in hash_map.items():
            if len(files) > 1:
                duplicates_found.append(files)
        
        if not duplicates_found:
            self.add_to_report("No duplicate files found!")
            self.print_report()
            return
        
        # Report and optionally remove duplicates
        removed_count = 0
        space_freed = 0
        
        for dup_group in duplicates_found:
            file_size = dup_group[0].stat().st_size
            self.add_to_report(f"\nDuplicate group ({len(dup_group)} files, {file_size:,} bytes each):")
            
            # Keep the first file, remove others
            for i, file_path in enumerate(dup_group):
                if i == 0:
                    self.add_to_report(f"  [KEEP] {file_path}")
                else:
                    if remove_duplicates:
                        try:
                            file_path.unlink()
                            self.add_to_report(f"  [REMOVED] {file_path}")
                            removed_count += 1
                            space_freed += file_size
                        except Exception as e:
                            self.add_to_report(f"  [ERROR] Could not remove {file_path}: {e}")
                    else:
                        self.add_to_report(f"  [DUPLICATE] {file_path}")
        
        total_duplicates = sum(len(group) - 1 for group in duplicates_found)
        self.add_to_report(f"\nSummary:")
        self.add_to_report(f"  Duplicate groups found: {len(duplicates_found)}")
        self.add_to_report(f"  Total duplicate files: {total_duplicates}")
        
        if remove_duplicates:
            self.add_to_report(f"  Files removed: {removed_count}")
            self.add_to_report(f"  Space freed: {space_freed:,} bytes ({space_freed / (1024**2):.2f} MB)")
        
        self.print_report()


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_valid_directory():
    """Get and validate directory path from user"""
    while True:
        directory = input("Enter directory path: ").strip().strip('"').strip("'")
        if os.path.isdir(directory):
            return directory
        print(f"Error: '{directory}' is not a valid directory. Please try again.")


def main():
    """Main menu interface"""
    manager = FileManager()
    
    while True:
        clear_screen()
        print("="*60)
        print("FILE MANAGEMENT AUTOMATION TOOL".center(60))
        print("="*60)
        print("\n1. Bulk Rename Files")
        print("2. Sort Files into Categories")
        print("3. Find Duplicate Files")
        print("4. Remove Duplicate Files")
        print("5. Exit")
        print("\n" + "="*60)
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == '1':
            clear_screen()
            print("BULK RENAME FILES")
            print("-" * 60)
            directory = get_valid_directory()
            pattern = input("Enter pattern to replace: ").strip()
            replacement = input("Enter replacement text: ").strip()
            regex_choice = input("Use regex matching? (y/n): ").strip().lower()
            use_regex = regex_choice == 'y'
            
            print("\nProcessing...")
            manager.bulk_rename(directory, pattern, replacement, use_regex)
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            clear_screen()
            print("SORT FILES INTO CATEGORIES")
            print("-" * 60)
            directory = get_valid_directory()
            
            print("\nProcessing...")
            manager.sort_files(directory)
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            clear_screen()
            print("FIND DUPLICATE FILES")
            print("-" * 60)
            directory = get_valid_directory()
            
            print("\nScanning for duplicates...")
            manager.find_duplicates(directory, remove_duplicates=False)
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            clear_screen()
            print("REMOVE DUPLICATE FILES")
            print("-" * 60)
            directory = get_valid_directory()
            
            confirm = input("\n⚠ WARNING: This will permanently delete duplicate files!\nContinue? (yes/no): ").strip().lower()
            if confirm == 'yes':
                print("\nScanning and removing duplicates...")
                manager.find_duplicates(directory, remove_duplicates=True)
            else:
                print("Operation cancelled.")
            
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            print("\nThank you for using File Management Tool!")
            sys.exit(0)
        
        else:
            input("\nInvalid option. Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)