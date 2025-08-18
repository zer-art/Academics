import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
import pickle
from PIL import Image
import io

# Configure Streamlit page
st.set_page_config(
    page_title="Traffic Sign Detection",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the trained model and label encoder
@st.cache_resource
def load_model_and_encoder():
    """Load the trained CNN model and label encoder"""
    try:
        model = tf.keras.models.load_model("traffic_sign_cnn.h5")
        with open("label_encoder.pkl", "rb") as f:
            label_encoder = pickle.load(f)
        return model, label_encoder
    except Exception as e:
        st.error(f"Error loading model or label encoder: {str(e)}")
        return None, None

def preprocess_image(image, target_size=(64, 64)):
    """Preprocess uploaded image for prediction"""
    # Convert PIL image to numpy array
    img_array = np.array(image)
    
    # Convert to RGB if needed
    if len(img_array.shape) == 3 and img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    elif len(img_array.shape) == 3 and img_array.shape[2] == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    
    # Resize image
    img_resized = cv2.resize(img_array, target_size)
    
    # Normalize pixel values
    img_normalized = img_resized / 255.0
    
    # Add batch dimension
    img_batch = np.expand_dims(img_normalized, axis=0)
    
    return img_batch

def predict_traffic_sign(image, model, label_encoder):
    """Predict traffic sign from image"""
    try:
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Make prediction
        predictions = model.predict(processed_image)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        
        # Get class label
        predicted_label = label_encoder.inverse_transform([predicted_class_idx])[0]
        
        return predicted_label, confidence, predictions[0]
    except Exception as e:
        st.error(f"Error during prediction: {str(e)}")
        return None, None, None

# Main application
def main():
    # Load model and encoder
    model, label_encoder = load_model_and_encoder()
    
    if model is None or label_encoder is None:
        st.error("Failed to load model or label encoder. Please check if the files exist.")
        st.stop()
    
    # Title and description
    st.title("🚦 Traffic Sign Detection System")
    st.markdown("""
    This application uses a Convolutional Neural Network (CNN) to detect and classify traffic signs.
    Upload an image containing a traffic sign to get predictions.
    """)
    
    # Sidebar for information
    with st.sidebar:
        st.header("📋 Model Information")
        st.info(f"**Classes Available:** {len(label_encoder.classes_)}")
        
        with st.expander("View All Classes"):
            for i, class_name in enumerate(label_encoder.classes_):
                st.write(f"{i+1}. {class_name}")
        
        st.header("🔧 Settings")
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Minimum confidence level for valid predictions"
        )
        
        show_top_predictions = st.checkbox(
            "Show Top 5 Predictions",
            value=True,
            help="Display top 5 predictions with confidence scores"
        )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image containing a traffic sign"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Predict button
            if st.button("🔍 Detect Traffic Sign", type="primary"):
                with st.spinner("Analyzing image..."):
                    predicted_label, confidence, all_predictions = predict_traffic_sign(
                        image, model, label_encoder
                    )
                    
                    if predicted_label is not None:
                        # Store results in session state for display in col2
                        st.session_state.prediction_results = {
                            'label': predicted_label,
                            'confidence': confidence,
                            'all_predictions': all_predictions,
                            'threshold': confidence_threshold,
                            'show_top': show_top_predictions
                        }
    
    with col2:
        st.header("🎯 Prediction Results")
        
        if 'prediction_results' in st.session_state:
            results = st.session_state.prediction_results
            predicted_label = results['label']
            confidence = results['confidence']
            all_predictions = results['all_predictions']
            
            # Main prediction result
            if confidence >= results['threshold']:
                st.success(f"**Detected Traffic Sign:** {predicted_label}")
                st.metric("Confidence", f"{confidence:.2%}")
            else:
                st.warning(f"**Low Confidence Detection:** {predicted_label}")
                st.metric("Confidence", f"{confidence:.2%}")
                st.info(f"Confidence is below threshold ({results['threshold']:.0%})")
            
            # Progress bar for confidence
            st.progress(confidence)
            
            # Top predictions
            if results['show_top']:
                st.subheader("📊 Top 5 Predictions")
                
                # Get top 5 predictions
                top_indices = np.argsort(all_predictions)[::-1][:5]
                
                for i, idx in enumerate(top_indices):
                    class_name = label_encoder.inverse_transform([idx])[0]
                    prob = all_predictions[idx]
                    
                    # Create a nice display for each prediction
                    col_rank, col_name, col_conf = st.columns([0.5, 2, 1])
                    
                    with col_rank:
                        st.write(f"**{i+1}.**")
                    with col_name:
                        st.write(class_name)
                    with col_conf:
                        st.write(f"{prob:.1%}")
                    
                    # Add progress bar for top prediction
                    if i == 0:
                        st.progress(prob)
                    else:
                        st.progress(prob, help=f"Confidence: {prob:.1%}")
        else:
            st.info("Upload an image and click 'Detect Traffic Sign' to see results here.")
    
    # Additional information section
    st.markdown("---")
    st.header("ℹ️ About the Model")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Input Size", "64×64 pixels")
    
    with col2:
        st.metric("Model Type", "CNN")
    
    with col3:
        st.metric("Classes", f"{len(label_encoder.classes_)}")
    
    with st.expander("Model Architecture Details"):
        st.markdown("""
        The model architecture consists of:
        - **3 Convolutional layers** with ReLU activation
        - **MaxPooling layers** for dimensionality reduction
        - **Fully connected layers** with dropout for regularization
        - **Softmax output layer** for multi-class classification
        
        The model was trained on traffic sign images with bounding box annotations.
        """)

if __name__ == "__main__":
    main()