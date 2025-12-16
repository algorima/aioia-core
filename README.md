aioia-core/
  ai_ml/
    fraud_detection/
      app/
        main.py                 # FastAPI entry
        api/
          routes.py             # endpoints
          schemas.py            # Pydantic request/response
        services/
          preprocess_text.py
          preprocess_image.py
          storage.py
          llm_client.py
          ensemble.py
        models/
          custom_model.py       # PyTorch model wrapper
          custom_model_ckpt/    # (gitignore)
      scripts/
        train_custom_model.py
        eval_custom_model.py
        download_models.py
      tests/
        test_preprocess.py
      Dockerfile
      requirements.txt
      README.md
  .gitignore
