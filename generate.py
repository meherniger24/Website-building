from enum import Enum
import os
from bs4 import BeautifulSoup
import shutil


STYLE_ASSETS = [
  'font-awesome/css/font-awesome.css' ,
  'bootstrap.min.css',
  'style.css'
]

class FontAwesomeIcons(str, Enum):
  NONE        = ""
  PDF         = "fa fa-fw fa-file-pdf-o"
  ENVELOPE    = "fa fa-fw fa-envelope"
  ARCHIVE     = "fa fa-fw fa-archive"
  BOOK        = "fa fa-fw fa-book"
  GITHUB      = "fa fa-fw fa-github"
  ZIP         = "fa fa-fw fa-file-archive-o"
  CODE        = "fa fa-fw fa-file-code-o"
  COPY        = "fa fa-fw fa-clipboard"
  GLOBE       = "fa fa-fw fa-globe"
  BACK_ARROW  = "fa fa-fw fa-long-arrow-left"
  GRAD_CAP    = "fa fa-fw fa-graduation-cap"
  MAP_MARKER  = "fa fa-fw fa-map-marker"
  FILE        = "fa fa-fw fa-file"
  LINKEDIN    = "fa fa-fw fa-linkedin-square"
  NEWS        = "fa fa-fw fa-newspaper-o"
  DOWNLOAD    = "fa-solid fa-chevron-down"

  def __str__(self):
    return self.value

class Person:
  def __init__(self, name, website, me = False):
    self.name = name
    self.website = website
    self.me = me 

class Publication:
  def __init__(self, 
               image, 
               title, 
               url,
               authors = [], 
               joint_authors = {},
               venue = '', 
               award = ''):
    self.image = image
    self.title = title
    self.url = url 
    self.authors = authors 
    self.joint_authors = joint_authors
    self.venue = venue
    self.award = award

  def get_author_suffix(self, author):
    suffix = ''
    for contribution_suffix, authors in self.joint_authors.items():
      if author in authors:
        suffix = contribution_suffix
    return suffix

  def get_author_names(self):
    names = ''
    for i, author in enumerate(self.authors):
      name = author.name
      name += self.get_author_suffix(author)

      if (author.me):
        names += f'<b>{name}</b>'

      elif (len(author.website) > 0):
        names += f'<a href={author.website}>{name}</a>'

      else:
        names += name
      
      if i == len(self.authors) - 2:
        names += ", "
      elif i < len(self.authors) - 1:
        names += ", "

    return names

class ProjectResources:
  def __init__(self, publication = [], code = []):
    self.publication = publication
    self.code = code

class Resource:
  def __init__(self, icon = FontAwesomeIcons.NONE, path = '', name = ''):
    self.icon = icon
    self.path = path
    self.name = name

class Course:
  def __init__(self, image, name, url, role, details):
    self.image = image
    self.name = name
    self.url = url
    self.role = role
    self.details = details

class Video:
  def __init__(self, name, id):
    self.name = name
    self.id = id

class AboutMe:
  def __init__(self, name, image, resources):
    self.name = name
    self.image = image
    self.resources = resources

  def get_html(self):
    links = ''
    for resource in self.resources:
      links += f'''
        <div class="d-block profile-row">
          <i class="{resource.icon}"></i>
          <a
            class="pl-2"
            href="{resource.path}"
          >
            {resource.name}
          </a>
        </div>
      '''
    return f'''
      <div class="d-flex pl-5 pt-5 justify-content-start">
        <div>
          <img
            id="profile-pic"
            class="float-left"
            src="{self.image}"
            alt="Bailey"
          />
        </div>
        <div class="col">
          <div class="d-block profile-row">
            <h1>{self.name}</h1>
          </div>
          {links}
        </div>
      </div>
    '''

class Home:
  def __init__(self, about_me, bio, publications = [], courses = [], ongoing_projects=[]):
    self.about_me = about_me
    self.bio = bio
    self.publications = publications 
    self.courses = courses
    self.ongoing_projects = ongoing_projects
    
  def get_ongoing_projects_html(self):
    project_list = ''
    for project in self.ongoing_projects:
        # Use main image if defined, else first image from the list, else use placeholder
        thumbnail = project.image or (project.images[0] if project.images else 'assets/default_placeholder.png')

        # Optionally display a video icon if videos exist
        video_icon = '<i class="fas fa-video ml-2"></i>' if project.videos else ''

        project_list += f'''
            <div>
                <div class="d-flex flex-row pb-4 align-items-center">
                    <img
                        src="{thumbnail}"
                        class="thumbnail img-responsive"
                        style="max-width: 150px; height: auto;"
                    />
                    <div class="d-flex flex-column pl-4">
                        <span>
                            <a href="{project.url}" class="item-title">{project.title}{video_icon}</a>
                        </span>
                    </div>
                </div>
            </div>
        '''
    return project_list


  

  def get_publications_list_html(self):
    pub_list = ''
    for _, pub in self.publications.items():
      pub_award_text = f'''<div class="paper-award">{pub.award}</div>'''
      pub_list += f'''
        <div>
          <div class="d-flex flex-row pb-4 align-items-center">
            <img
              src={pub.image}
              class="thumbnail img-responsive"
            />
            <div class="d-flex flex-column pl-4">
              <span>
                <a href={pub.url} class="item-title">{pub.title}</a>
              </span>
              <div>
                {pub.get_author_names()}
              </div>
              <div>
                {pub.venue}
              </div>
              <div>
                {pub_award_text if pub.award else ''}
              </div>
            </div>
          </div>
        </div>
      '''
    return pub_list

  def get_teaching_list_html(self):
    teaching_list = ''
    for course in self.courses:
      teaching_list += f'''
        <div>
          <div class="d-flex flex-row pb-4 align-items-center">
            <img
              src={course.image}
              class="thumbnail img-responsive"
            />
            <div class="d-flex flex-column pl-4">
              <span>
                <a href={course.url} class="item-title">{course.name}</a>
              </span>
              <div>
                <b>{course.role}</b>
              </div>
              <div>
                {course.details}
              </div>
            </div>
          </div>
        </div>
      '''
    return teaching_list
  def generate(self, path):
    soup = BeautifulSoup('<!DOCTYPE html> <html></html>', 'html.parser')

    # Add styling 
    head = soup.new_tag('head')
    soup.html.append(head)

    head.append(soup.new_tag('meta', charset="UTF-8"))
    links = [
        soup.new_tag('link', rel='stylesheet', type='text/css', 
                     href=os.path.join('assets', style_asset))
        for style_asset in STYLE_ASSETS
    ]
    [head.append(link) for link in links]

    # Construct page
    body = soup.new_tag('body')
    soup.html.append(body)
    about_me_section = self.about_me.get_html()
    publications_list = self.get_publications_list_html()
    ongoing_projects_list = self.get_ongoing_projects_html()  
    teaching_list = self.get_teaching_list_html()
    body.append(BeautifulSoup(f''' 
      <div class="container">
        {about_me_section} 
      </div>
      <div class="container">
        <div class="d-flex flex-column pl-5 pt-3">
          <div>
            <p>{self.bio}</p>
          </div>
          <div>
            <h4>Publications</h4>
            <hr/>
            {publications_list}
            <div class="pb-5"></div>
            </div>
            <div>
              <h4>Ongoing Projects</h4>
              <hr/>
              {ongoing_projects_list} 
             </div>
             <div>
            <h4>Teaching</h4>
            <hr/>
            {teaching_list}
          </div>
        </div>
        <br>
        <div class="text-center">
          <h6 class="font-weight-light"> 
            Source code for this website is <a href=https://github.com/meherniger24>available on Github</a>
          </h6>
        </div>
      </div>
    ''', 'html.parser'))
    with open(os.path.join(path, 'index.html'), "w", encoding="utf-8") as file:
        file.write(str(soup))

class OngoingProject:
    def __init__(self, image='', title='', url='', details=[], videos=[], images=[]):
        self.image = image  # Main preview image (optional)
        self.title = title
        self.url = url
        self.details = details  # List of description points
        self.videos = videos    # List of video paths
        self.images = images    # List of image paths

    def generate(self, path):
        """Generates the HTML for this project."""
        # Convert details into a bulleted list
        details_html = '<ul>'
        for detail in self.details:
            details_html += f'<li>{detail}</li>'
        details_html += '</ul>'

        # Render videos
        videos_html = ''
        for video in self.videos:
            videos_html += f'''
                <div class="mt-3 mb-3">
                    <h4 class="font-weight-light">Video</h4>
                    <video controls class="embed-responsive-item project-video" style="max-width: 100%; height: auto;">
                        <source src="{video}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
            '''

        # Render additional images
        images_html = ''
        for img in self.images:
            images_html += f'''
                <div class="mt-3 mb-3">
                    <h4 class="font-weight-light">Image</h4>
                    <img src="{img}" alt="Project image" style="max-width: 100%; height: auto;" class="img-fluid">
                </div>
            '''

        # Use BeautifulSoup to build HTML
        soup = BeautifulSoup('<!DOCTYPE html> <html></html>', 'html.parser')

        head = soup.new_tag('head')
        soup.html.append(head)
        head.append(soup.new_tag('meta', charset="UTF-8"))
        links = [
            soup.new_tag('link', rel='stylesheet', type='text/css',
                         href=os.path.join('../../assets', style_asset))
            for style_asset in STYLE_ASSETS
        ]
        [head.append(link) for link in links]

        body = soup.new_tag('body')
        soup.html.append(body)
        body.append(BeautifulSoup(f'''
            <div class="container">
                <nav class="navbar navbar-expand-lg">
                    <div class="container-fluid">
                        <ul class="navbar-nav ml-auto">
                            <li class="nav-item"> 
                                <a href="../../">
                                <i class="{FontAwesomeIcons.BACK_ARROW}"></i>
                                Home
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>
                <h1 class="card-title font-weight-normal">{self.title}</h1>

                <h4>Description:</h4>
                {details_html}
                {images_html}
                {videos_html}
            </div>
        ''', 'html.parser'))

        # Save the HTML file
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, 'index.html'), "w", encoding="utf-8") as file:
            file.write(str(soup))


class Project:
  def __init__(self, 
               image,
               image_caption, 
               abstract, 
               videos = [], 
               resources = ProjectResources(), 
               acknowledgements= '', 
               citation = ''):
    self.image = image
    self.image_caption = image_caption
    self.abstract = abstract
    self.videos = videos
    self.resources = resources
    self.acknowledgements = acknowledgements
    self.citation = citation

  def create_section(self, name, content):
    return f'''
      <div>
        <h2 class="mt-4 font-weight-normal">{name}</h2>
        <hr>
        {content}
      </div>
    '''

  def create_resources_list(self, name, resources):
    resources_list = ''
    for resource in resources:
      resources_list += f'''
        <div class="container mt-1 mb-1">
          <i class="{resource.icon}"></i>
          <a href="{resource.path}">
            {resource.name}
          </a>
        </div>
        '''
    return f'''
      <div>
        <h4 class="mt-4 font-weight-light">
          {name}
        </h4>
        {resources_list}
      </div>
    '''
    


  def get_abstract_html(self):
    if len(self.abstract) == 0:
      return ''
    return self.create_section('Abstract', f'<p>{self.abstract}</p>')

  def get_video_html(self):
    if len(self.videos) == 0:
        return ''

    video_list = '<div class="container">'
    video_list += '<h2 class="mt-4 font-weight-normal">Visualization</h2><hr>'

    for i in range(0, len(self.videos), 2):
        video_list += '<div class="row">'

        # First video
        video_list += f'''
            <div class="col-md-6">
                <h4 class="font-weight-light">{self.videos[i].name}</h4>
                <video class="autoplay-video embed-responsive-item project-video" 
                       width="100%" muted loop playsinline>
                    <source src="{self.videos[i].id}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
        '''

        # Second video (if exists)
        if i + 1 < len(self.videos):
            video_list += f'''
                <div class="col-md-6">
                    <h4 class="font-weight-light">{self.videos[i + 1].name}</h4>
                    <video class="autoplay-video embed-responsive-item project-video" 
                           width="100%" muted loop playsinline>
                        <source src="{self.videos[i + 1].id}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
            '''

        video_list += '</div>'  # Close row

    video_list += '</div>'  # Close container

    # Add JavaScript to force autoplay
    video_list += '''
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            let videos = document.querySelectorAll(".autoplay-video");
            videos.forEach(video => {
                video.play().catch(error => {
                    console.log("Autoplay prevented. User interaction required.");
                });
            });
        });
    </script>
    '''
    
    return self.create_section('Visualization', video_list)

  def get_resources_html(self):
    resources_html = ''

    if len(self.resources.publication) > 0:
      resources_html += self.create_resources_list('Publication', self.resources.publication)
    
    if len(self.resources.code) > 0:
      resources_html += self.create_resources_list('Code', self.resources.code)

    return self.create_section('Resources', resources_html)

  def get_acknowledgements_html(self):
    if len(self.acknowledgements) == 0:
      return ''
    return self.create_section('Acknowledgements', f'<p>{self.acknowledgements}</p>')

  def get_citation_html(self):
    if len(self.citation) == 0:
      return ''

    return self.create_section('Cite', f'''
      <script>
      function copyText() {{
        var text = document.getElementById("citation-to-copy")
        navigator.clipboard.writeText(text.innerText)
      }}
      </script>
      <div class="code-background">
        <button class="code-copy-btn" onClick=copyText()>
          <i class="{FontAwesomeIcons.COPY}"></i>
        </button>
        <pre id="citation-to-copy">
        {self.citation}</pre>
      </div>
      '''
    )

  def generate(self, path, publication):
    soup = BeautifulSoup('<!DOCTYPE html> <html></html>', 'html.parser')

    # Add styling
    head = soup.new_tag('head')
    head.append(soup.new_tag('meta', charset="UTF-8"))
    soup.html.append(head)
    links = [
        soup.new_tag('link', rel='stylesheet', type='text/css', 
                     href=os.path.join('../../assets', style_asset))
        for style_asset in STYLE_ASSETS
    ]
    [head.append(link) for link in links] 

    # Construct body
    body = soup.new_tag('body')
    soup.html.append(body)
    
    # Copy videos into the project directory
    video_paths = []
    for video in self.videos:
        video_filename = os.path.basename(video.id)
        video_dest = os.path.join(path, video_filename)
        
        # Copy video only if it doesn't exist in the destination folder
        if not os.path.exists(video_dest):
            shutil.copy(video.id, video_dest)

        video_paths.append(video_filename)  # Store correct video path

    # Generate video HTML (two videos per row)
    videos_html = '<div class="container">'
    videos_html += '<h2 class="mt-4 font-weight-normal">Visualization</h2><hr>'

    for i in range(0, len(video_paths), 2):
        videos_html += '<div class="row">'

        # First video
        videos_html += f'''
            <div class="col-md-6">
                <h4 class="font-weight-light">{self.videos[i].name}</h4>
                <video controls class="embed-responsive-item project-video" width="100%">
                    <source src="{video_paths[i]}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
        '''

        # Second video (if exists)
        if i + 1 < len(video_paths):
            videos_html += f'''
                <div class="col-md-6">
                    <h4 class="font-weight-light">{self.videos[i + 1].name}</h4>
                    <video controls class="embed-responsive-item project-video" width="100%">
                        <source src="{video_paths[i + 1]}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
            '''

        videos_html += '</div>'  # Close row

    videos_html += '</div>'  # Close container

    # Add the full page content
    body.append(BeautifulSoup(f'''
      <div class="container">
        <nav class="navbar navbar-expand-lg">
          <div class="container-fluid">
            <ul class="navbar-nav ml-auto">
              <li class="nav-item"> 
                <a href="../../">
                <i class="{FontAwesomeIcons.BACK_ARROW}"></i>
                home
                </a>
              </li>
            </ul>
          </div>
        </nav>
        <h1 class="card-title font-weight-normal">{publication.title}</h1>
        <h4 class="font-weight-light">{publication.get_author_names()}</h4>
        <img src="{self.image}" class="card-img-top mt-3" alt="{publication.title}-teaser">
        <p class="font-italic mt-2">{self.image_caption}</p>
        {self.get_abstract_html()}
        {videos_html}  <!-- Embedded videos appear here -->
        {self.get_resources_html()}
        {self.get_citation_html()}
        {self.get_acknowledgements_html()}
      </div>
    ''', 'html.parser'))

    # Ensure directory exists
    if not os.path.exists(path):
        os.makedirs(path)

    # Write the final HTML file
    with open(os.path.join(path, 'index.html'), "w", encoding="utf-8") as file:
        file.write(str(soup))

PEOPLE = {
  'your-name': Person(
    name = 'Meher Niger',
    website = '',
    me = True
  ),
  'coauthor-name': Person(
    name = 'W Moree, M Bluhm, J Eriksen, G Chen, D Mayerich',
    website = ''
  ),
  'coauthor-name-other': Person(
    name = 'H Goharbavang, A Pillai, JD Wythe, G Chen, D Mayerich',
    website = ''
  ),
  'coauthor-name-other2': Person(
    name = 'Mohammad Istiaque Reja, Jobaida Akhtar, Nishat Jahan, Rubaya Absar, Saleha Fatema',
    website = ''
  ),
  'coauthor-name-other3': Person(
    name = 'Tazkia Fairuz Hasin',
    website = ''
  ),
  'coauthor-name-other4': Person(
    name = 'Tazkia Fairuz Hasin, Mohammed Abu Faiz Nizami, Muhammad Alam Rafee',
    website = ''
  )
}

ABOUT_ME = AboutMe(
  name = 'Meher Niger',
  image = 'data/images/profile1.jpg', 
  resources=[
    Resource(
      icon=FontAwesomeIcons.MAP_MARKER,
      name='University of Houston',
      path='https://www.uh.edu'
    ),
    Resource(
      icon=FontAwesomeIcons.ENVELOPE,
      name='mehernigeretho@gmail.com',
      path='mailto:mehernigeretho@gmail.com'
    ),
    Resource(
      icon=FontAwesomeIcons.GITHUB,
      name='Github',
      path='https://github.com/meherniger24'
    ),
    Resource(
      icon=FontAwesomeIcons.GRAD_CAP,
      name='Google Scholar',
      path='https://scholar.google.com/citations?user=VnKZqyIAAAAJ&hl=en&oi=ao'
    ),
    Resource(
      icon=FontAwesomeIcons.GRAD_CAP,
      name='Linkedin',
      path='https://www.linkedin.com/in/meher-niger-84177bb1/'
    ),
    Resource(
      icon=FontAwesomeIcons.FILE,
      name='CV',
      path='data/documents/cv.pdf'
    )
  ]
)

BIO = '''I'm a fifth year Ph.D. student at University of Houston where I'm advised by Dr. <a href="https://www.ece.uh.edu/faculty/mayerich/">David Mayerich</a>. My current research focuses on creating GPU-accelerated algorithms, computational methods for modeling, analyzing and visualizing gigavoxel-scale data. I have also developed computational methods for sparse volumetric microvasculature in OpenVDB optimized with TBB multithreading parallelism. Currently, I am working on a deep learning based 3D Stardist model to detect specific kinds of nuclei AND Developing A fully parallel 3D thinning algorithm for giga-voxel scale microvasculature using OpenVDB. My work is supported by the NSF Graduate Research Fellowship. I received a B.Sc in Electrical and Electronics Enginnering at Chittagong University of Engineering and Technology, Bangladesh, where my research focus was on Photonic Crystal Fiber.'''

PUBLICATIONS = {
  'pub1': Publication(
    image =  'data/images/thumbnails/liver.png',
    title =  'SEGMENTATION OF MICROVASCULAR NETWORKS EMBEDDED IN GIGAVOXEL 3D IMAGES USING RSF LEVEL SETS WITH OPENVDB',
    url = 'project/pub1',
    authors =  [
      PEOPLE['your-name'],
      PEOPLE['coauthor-name'],
    ],
    venue = '2025 IEEE International Symposium on Biomedical Imaging (ISBI 2025)',
  ),
  'pub2': Publication(
    image =  'data/images/thumbnails/KESM.jpg',
    title =  'GPU-Accelerated RSF Level Set Evolution for Large-Scale Microvascular Segmentation',
    url = 'project/pub2',
    authors =  [
      PEOPLE['your-name'],
      PEOPLE['coauthor-name-other']
    ],
    venue = 'Cell Reports Methods',
  ),
  
  'pub3': Publication(
    image =  'data/images/thumbnails/pub3.JPG',
    title =  'Modified Dodecagonal PCF Sensor with High Sensitivity for Detecting Harmful Chemical Compounds used in Poultry Feed',
    url = 'https://ieeexplore.ieee.org/abstract/document/8975607/',
    authors =  [
      PEOPLE['your-name'],
      PEOPLE['coauthor-name-other2']
    ],
    venue = '2019 5th International Conference on Advances in Electrical Engineering (ICAEE)',
  ),
  'pub4': Publication(
    image =  'data/images/thumbnails/pub4.JPG',
    title =  'Detection of harmful chemical compounds in plastics with highly sensitive photonic crystal fiber with higher nonlinear coefficient',
    url = 'https://ieeexplore.ieee.org/abstract/document/9065165/',
    authors =  [
      PEOPLE['your-name'],
      PEOPLE['coauthor-name-other3']
    ],
    venue = '2019 IEEE International Conference on Signal Processing, Information, Communication & Systems (SPICSCON)',
  ),
  
  'pub5': Publication(
    image =  'data/images/thumbnails/pub5.JPG',
    title =  'Three modified structures of photonic crystal fiber for estimation of sulfuric acid concentration with low confinement Loss and negative dispersion',
    url = 'https://ieeexplore.ieee.org/abstract/document/9068781/',
    authors =  [
      PEOPLE['your-name'],
      PEOPLE['coauthor-name-other4']
    ],
    venue = '2019 4th International Conference on Electrical Information and Communication Technology (EICT)',
  )
}

video1 = Video(name="Ongoing Project 1 Demo", id="ongoing/pro1/video.mp4")

ONGOING_PROJECTS = [
    
    
    OngoingProject(
        image='data/images/thumbnails/skele.JPG',
        title='An End-to-End Pipeline for Vascular Network Extraction and Quantitative Characterization: Segmentation, Skeletonization, and Comparative Benchmarking',
        #description='Description of ongoing project 2.',
        details=[
            "I have been developing an integrated software framework that combines segmentation, skeletonization, and quantitative vascular analysis into a single pipeline. This framework enables automated vessel extraction, graph-based skeleton representation, and computation of key descriptors such as radius, tortuosity, curvature, volume, and surface area. By linking voxel-level image processing with graph-based modeling, my work bridges the gap between raw image data and clinically meaningful biomarkers. To support this framework, I designed custom data structures in C++ for efficient representation of vascular graphs, nodes, and edges, enabling scalable analysis of large volumetric datasets. These data structures were optimized for memory efficiency and integrated seamlessly with high-performance computing libraries such as OpenVDB and TBB. In addition, I developed visualization and interactive analysis tools using OpenGL and Dear ImGui, which allow real-time rendering, editing, and exploration of vascular networks."
            "  3D Visualization is coming soon....."
        ],
        url = 'ongoing/pro2',
        #videos=["video.mp4"]
    ),
    
    
    OngoingProject(
        image='data/images/thumbnails/stardist.JPG',
        title='Cell segmentation with Deep Learning based StarDist 3D',
        details=[
            "I am working on a deep learning-based Stardist 3D model to segment individual cells. To facilitate this, I developed a GUI using PyQt to manually label each cell with its corresponding name, enabling the preparation of high-quality training data.",
            "The GUI includes several features:"
            "Data Loading: It supports loading two volumes (raw and segmented) along with a text file containing class IDs and their corresponding names. The text file can be edited or modified as needed, and the GUI automatically updates the cell IDs and names upon loading.",
            "Zoom and Transparency: Users can zoom in and out for detailed cell examination and adjust the transparency level between the raw and segmented volumes for better visualization.",
            "Cell Viewing Options: The GUI allows users to view only labeled cells, unlabeled cells, or all cells at once."
            "Data Saving: The final labeled cells can be saved in .npy or .txt format for further use. This tool streamlines the process of annotating cells and ensures the creation of accurate training data for deep learning models.."
            "A video of the GUI has been provided for reference."
        ],
        url = 'ongoing/pro1',
        videos=["video.mp4"]
    ), 
    OngoingProject(
        image='data/images/thumbnails/Picture1.jpg',
        title='Weak to Strong Segmentation',
        
        url = 'ongoing/pro3',
        #videos=["video.mp4"]
    )
    
]


COURSES = [
    Course(
      image = 'data/images/thumbnails/numerical.jpg',
      name = 'Numerical Methods for Electrical and Computer Engineers',
      url = 'https://www.uh.edu',
      role = 'Teaching Assistant',
      details = 'UH, ECE, Spring 2024'
    ),
    
  Course(
    image = 'data/images/thumbnails/antenna.JPG',
    name = 'Antenna Engineering',
    url = 'https://www.uh.edu',
    role = 'Teaching Assistant',
    details = 'UH, ECE, Spring 2021'
  ),
  Course(
    image = 'data/images/thumbnails/robotics.JPG',
    name = 'Intro to Robotics',
    url = 'https://www.uh.edu',
    role = 'Teaching Assistant',
    details = 'UH, ECE, Fall 2020'
  ),
  Course(
    image = 'data/images/thumbnails/tele.jpg',
    name = 'Advanced Telecommunication',
    url = 'https://www.uh.edu',
    role = 'Teaching Assistant',
    details = 'UH, ECE, Fall 2020'
  )
]

PROJECT_PAGES = {
  'pub1': Project(
    image = '../../data/images/liver.png',
    image_caption = 'Liver vasculature imaged using MUVE. (a-b) Front and back view of the reconstruction from 1500 slices and (c-g) several iterated higher-resolution zooms.',
    abstract = 'Microvascular networks are vital for tissue function and disease progression, but their complex three-dimensional structure makes them difficult to analyze. Recent milling- based microscopy methods can capture images of these networks in whole organs at high resolution, though the resulting gigavoxel-scale images are challenging to segment. Convolutional neural networks (CNNs) are commonly used for this task, but they cannot account for the networks shape and topology. This paper presents a solution using a fully auto-mated milling microscope to create a gigavoxel-scale dataset of mouse liver microvasculature. A CNN is trained to create an initial segmentation of the vascular network. The vessels are then refined using a parallel RSF-based level set model. To make this model practical on such large volumes, it is implemented in parallel using a sparse OpenVDB data structure that reduces the grid size to approxately 4% of the original.',
    resources = ProjectResources(
      publication = [
        Resource(
          icon = FontAwesomeIcons.PDF,
          path = 'https://scholar.google.com/citations?view_op=view_citation&hl=en&user=VnKZqyIAAAAJ&citation_for_view=VnKZqyIAAAAJ:UeHWp8X0CEIC',
          name = 'Paper'
        ),
        #Resource(
        #  icon = FontAwesomeIcons.BOOK,
         # path = 'https://www.acm.org/',
        #  name =  'Publisher\'s Version'
        #),
        #Resource(
       #   icon =  FontAwesomeIcons.ARCHIVE,
       #   path =  'https://arxiv.org',
       #   name =  'ArXiv Version'
       # )
      ],
      code = [
        Resource(
          icon =  FontAwesomeIcons.GITHUB,
          path =  'https://github.com/meherniger24/paper-rsf-openvdb',
          name = 'Github project with full source code'
        )
      ],
    ),
    videos=[
            Video(name='Visualization of a vessel cube in openvdb vdb_view', id='docs/project/pub1/openvdb.mp4'),
           # Video(name='Evolution of the level set from 𝜙<sub>0</sub> to 𝜙<sub>n</sub></p> ', id='docs/project/pub1/video3.mp4')
            
        ],
   # videos = [
    #  Video(
    #    name =  'presentation slides',
    #    id = 'tjYVcOJONdI'
   #   )
   # ],
    #acknowledgements = 'This work was generously supported by XYZ',
    #citation = '''
    #@article{
     # Author:PAPER:2024,
     # title={Placeholder Title},
     # volume={42},
     # ISSN={1557-7368},
     # url={https://www.arxiv.org},
     # number={4},
     # journal={ACM Transactions on Graphics},
     # publisher={Association for Computing Machinery (ACM)},
     # authors={YourName}
     # year={2024},
     # month=jul, 
     # pages={1-100}
   # }'''
  ),
  
  'pub2': Project(
    image = '../../data/images/KESM.jpg',
    image_caption = 'Whole brain vasculature imaged using knife edge scanning microscopy (KESM) and available online (kesm.cs.tamu.edu)(a) Reconstruction from 140 slices across the whole brain is shown, along with (b) a 4000*2000*2000 voxel sub-volume with (c-e) several iterated higher-resolution zooms.',
    abstract = 'Microvascular networks are challenging to reconstruct because they are composed of individual structures near the resolution limit of existing microscopes, making boundary detection difficult. Machine learning tools like convolutional neural networks are effective at semantic segmentation, however they cannot leverage existing information about the global structure of these networks. Level sets are suitable for solving this problem, since they can integrate both the local tube-like structure of capillaries and globally complex topology. However active contours are computationally intensive, making them impractical for terabyte-scale images. We propose a highly parallel formulation of the region-scalable fitting (RSF) model, making it viable for three-dimensional gigavoxel images. We first train a U-Net to provide an initial contour, and then use the proposed RSF model to finalize the segmentation. We tested this approach on microvascular data acquired using multiple state-of-the-art imaging methods. We assess the performance using a Monte-Carlo validation technique and compare results to existing algorithms. This study showcases the practical application of the RSF model, emphasizing its utility in the challenging domain of large-scale high-topology network segmentation with a particular focus on building microvascular models.',
    resources = ProjectResources(
      publication = [
        Resource(
          icon = FontAwesomeIcons.PDF,
          path = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11037869/',
          name = 'Paper'
        ),
        #Resource(
        #  icon = FontAwesomeIcons.BOOK,
         # path = 'https://www.acm.org/',
        #  name =  'Publisher\'s Version'
        #),
        #Resource(
       #   icon =  FontAwesomeIcons.ARCHIVE,
       #   path =  'https://arxiv.org',
       #   name =  'ArXiv Version'
       # )
      ],
      code = [
        Resource(
          icon =  FontAwesomeIcons.GITHUB,
          path =  'https://github.com/meherniger24/paper-rsf-vesselseg',
          name = 'Github project with full source code'
        )
      ],
    ),
    videos=[
            Video(name='360&#176 rotation of the evolved 𝜙<sub>n</sub></p>', id='docs/project/pub1/video1.mp4'),
            Video(name='Evolution of the level set from 𝜙<sub>0</sub> to 𝜙<sub>n</sub></p> ', id='docs/project/pub1/video3.mp4')
            
        ],
   # videos = [
   #   Video(
   #     name =  'presentation slides',
   #     id = 'tjYVcOJONdI'
   #   )
   # ],
    #acknowledgements = 'This work was generously supported by XYZ',
    #citation = '''
    #@article{
     # Author:PAPER:2024,
     # title={Placeholder Title},
     # volume={42},
     # ISSN={1557-7368},
     # url={https://www.arxiv.org},
     # number={4},
     # journal={ACM Transactions on Graphics},
     # publisher={Association for Computing Machinery (ACM)},
     # authors={YourName}
     # year={2024},
     # month=jul, 
     # pages={1-100}
   # }'''
  )
}


if __name__ == '__main__':
    directory = 'docs/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    home = Home(
        about_me=ABOUT_ME, 
        bio=BIO, 
        publications=PUBLICATIONS,
        ongoing_projects=ONGOING_PROJECTS,
        courses=COURSES
    )
              
    home.generate(directory)
    
    for id, project in PROJECT_PAGES.items():
        project_path = os.path.join(directory, f'project/{id}')
        paper = PUBLICATIONS[id]
        project.generate(project_path, paper)

    # Generate ongoing project pages
    for ongoing_project in ONGOING_PROJECTS:
        project_path = os.path.join(directory, f'{ongoing_project.url}')
        ongoing_project.generate(project_path)


