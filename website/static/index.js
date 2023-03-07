function like(postId) {
    const likeCount = document.getElementById(`likes-count-${postId}`);
    const likeButton = document.getElementById(`like-button-${postId}`);
  
    fetch(`/like-post/${postId}`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        likeCount.innerHTML = data["likes"];
        if (data["liked"] === true) {
          likeButton.className = "bi bi-hand-thumbs-up-fill";
        } else {
          likeButton.className = "bi bi-hand-thumbs-up";
        }
      })
      .catch((e) => alert("Could not like post."));
  }