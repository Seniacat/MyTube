from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter
def comments_filter(comments_list, user_id):
    print(user_id)
    res = """
          <ul style="list-style-type:none;">
            <div class="col-md-12 mt-2">
              {}
            </div>
          </ul>
          """
    i = ''
    for comment in comments_list:
        id = comment['id']
        author = comment['author']
        if author.id == user_id:
            i += """
              <li>
                <div class="card shadow-lg p-2 mb-2 bg-white rounded">
                  <div class="card shadow-lg p-2 mb-2 bg-white rounded">
                    <h5 class="mt-0">{author}</h5>
                    <hr>
                    <p>{text}</p>
                  </div>
                  <span
                    class="reply"
                    data-id="{id}"
                    data-parent="{parent_id}"
                    style="color:blue;cursor:pointer;">
                      <small>Ответить</small>                    
                      <a href="/posts/{id}/comment_delete/">x</a>                    
                  </span>
                  </a>
                  <form
                    action=""
                    method="POST"
                    class="form-group mb-2"
                    id="form-{id}"
                    style="display:none;"
                  >
                    <textarea
                      type="text"
                      class="form-control"
                      name="comment-text"
                      id="{id}"></textarea>
                    <br>
                    <input
                      type="submit"
                      class="btn btn-primary submit-reply"
                      data-id="{id}"
                      data-submit-reply="{parent_id}"
                      value="Отправить"
                    >
                  </form>
                </div>
              </li>
              """.format(
                      id=comment['id'],
                      author=comment['author'],
                      text=comment['text'],
                      parent_id=comment['parent'],
                    )
        else:
            i += """
              <li>
                <div class="card shadow-lg p-2 mb-2 bg-white rounded">
                  <div class="card shadow-lg p-2 mb-2 bg-white rounded">
                    <h5 class="mt-0">{author}</h5>
                    <hr>
                    <p>{text}</p>
                  </div>
                  <span
                    class="reply"
                    data-id="{id}"
                    data-parent="{parent_id}"
                    style="color:blue;cursor:pointer;">
                      <small>Ответить</small>                    
                      
                  </span>
                  </a>
                  <form
                    action=""
                    method="POST"
                    class="form-group mb-2"
                    id="form-{id}"
                    style="display:none;"
                  >
                    <textarea
                      type="text"
                      class="form-control"
                      name="comment-text"
                      id="{id}"></textarea>
                    <br>
                    <input
                      type="submit"
                      class="btn btn-primary submit-reply"
                      data-id="{id}"
                      data-submit-reply="{parent_id}"
                      value="Отправить"
                    >
                  </form>
                </div>
              </li>
              """.format(
                      id=comment['id'],
                      author=comment['author'],
                      text=comment['text'],
                      parent_id=comment['parent'],
                    )
        if comment.get('children'):
            i += comments_filter(comment['children'])
    
    return mark_safe(res.format(i))
    

