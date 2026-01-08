import os
import sys
import json
import mimetypes
from cv_parser import parse_cv_multimodal
from cv_dividers_only import generate_divider, generate_divider_smaller, generate_divider_larger, generate_divider_tiny, create_circular_image_with_border
from email_sender import send_cvs_email

def main():
    # Usage: python main.py [client_folder_path]
    
    # 1. Input Handling: Folder Path
    folder_path = "input_samples/default_client"
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    
    if not os.path.exists(folder_path):
        print(f"Error: Client folder '{folder_path}' not found.")
        print("Usage: python main.py path/to/client_folder")
        return

    print(f"--- Processing Client Folder: {folder_path} ---")

    # 2. File Scanning & Classification
    input_files_for_gemini = []
    profile_image_path = None
    
    # Heuristics for profile picture:
    # - Named "foto", "profile", "perfil"
    # - OR is the only image and looks square-ish? (Simple approach: prefer explicitly named, else assume first image is photo if not a document)
    
    file_list = os.listdir(folder_path)
    for fname in file_list:
        full_path = os.path.join(folder_path, fname)
        if not os.path.isfile(full_path):
            continue
            
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type: 
            continue

        lower_name = fname.lower()
        
        # Check if it's an image
        if mime_type.startswith('image'):
            # Simple logic: If it has 'foto', 'perfil', 'profile' in name, use as profile pic
            # Otherwise treat as document (screenshot of old CV)
            if any(k in lower_name for k in ['foto', 'perfil', 'profile', 'face']):
                profile_image_path = full_path
                print(f"Found Profile Picture: {fname}")
            else:
                # If we don't have a profile pic yet, and this is an image, treat as potential content or photo
                # For now, let's treat generic images as content for Gemini (screenshots of text)
                # UNLESS it's the *only* image, then maybe it's the photo.
                # Let's keep it simple: Treat as content unless clearly named.
                # Use User rule: "foto de la persona" usually implies a separate file.
                input_files_for_gemini.append(full_path)
        else:
            # Text, PDF, etc. -> Send to Gemini
            input_files_for_gemini.append(full_path)

    if not input_files_for_gemini and not profile_image_path:
        print("No files found in folder to process.")
        return

    # 3. Multimodal Parsing
    print(f"Sending {len(input_files_for_gemini)} files to Gemini for parsing...")
    try:
        cv_data = parse_cv_multimodal(input_files_for_gemini)
        print("CV Data parsed successfully.")
        
        # Debug save
        with open(os.path.join(folder_path, "parsed_data_debug.json"), "w", encoding='utf-8') as f:
            json.dump(cv_data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Failed to parse CV data: {e}")
        return

    # 4. Image Processing for PDF
    processed_image_out = None
    if profile_image_path:
        print(f"Processing profile image: {profile_image_path}")
        # Save processed in the client folder
        clean_img_name = f"processed_{os.path.basename(profile_image_path)}"
        processed_image_path = os.path.join(folder_path, clean_img_name)
        # Note: changing extension to png in logic, make sure path handles it
        processed_image_out = os.path.splitext(processed_image_path)[0] + ".png"
        
        res = create_circular_image_with_border(profile_image_path, processed_image_out)
        if not res:
            print("Warning: Failed to process profile image.")
            processed_image_out = None

    # 5. PDF Generation
    output_dir = os.path.join(folder_path, "output_cvs")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Generating PDFs...")
    generated_pdfs = []
    try:
        path_n = generate_divider(cv_data, out_dir=output_dir, image_path=processed_image_out)
        path_s = generate_divider_smaller(cv_data, out_dir=output_dir, image_path=processed_image_out)
        path_l = generate_divider_larger(cv_data, out_dir=output_dir, image_path=processed_image_out)
        path_t = generate_divider_tiny(cv_data, out_dir=output_dir, image_path=processed_image_out)
        
        generated_pdfs = [path_n, path_s, path_l, path_t]
        print(f"PDFs created in: {output_dir}")
        
    except Exception as e:
        print(f"Error generating PDFs: {e}")
        return

    # 6. Email Delivery
    # Check env vars
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")
    
    candidate_email = cv_data.get("email")
    candidate_name = cv_data.get("nombre", "Candidato")

    if gmail_user and gmail_pass and candidate_email:
        print(f"Sending email to {candidate_email}...")
        send_cvs_email(candidate_email, generated_pdfs, candidate_name, gmail_user, gmail_pass)
    else:
        print("\n--- Skipping Email ---")
        if not candidate_email:
            print("Reason: No email found in parsed CV data.")
        elif not (gmail_user and gmail_pass):
            print("Reason: Gmail credentials (GMAIL_USER, GMAIL_APP_PASSWORD) not set in environment.")

if __name__ == "__main__":
    main()
