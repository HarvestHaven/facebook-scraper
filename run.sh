docker run -v $(pwd)/volumes:/var/volumes -v $(pwd)/post_list.json:/app/post_list.json fb_posts /var/volumes /app/post_list.json                                                                  
docker build -t fb_posts .
