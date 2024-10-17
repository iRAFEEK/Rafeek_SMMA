from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
import io, csv
from datetime import datetime
from app.models import User, Client, Task, OnboardingTask, ContentIdea, Metric, Notification
from app.forms import ClientForm, OnboardingTaskForm, ContentIdeaForm, MetricForm, TaskForm, TaskSubmissionForm, LoginForm, RegisterForm

main = Blueprint('main', __name__)

def get_unread_notification_count(user_id):
    return Notification.query.filter_by(user_id=user_id, read=False).count()

@main.context_processor
def inject_notification_count():
    if current_user.is_authenticated:
        unread_notification_count = get_unread_notification_count(current_user.id)
        return {'unread_notification_count': unread_notification_count}
    return {'unread_notification_count': 0}

@main.route('/')
@login_required
def index():
    if current_user.is_manager:
        return redirect(url_for('main.manager_dashboard'))
    else:
        return redirect(url_for('main.worker_dashboard'))

@main.route('/manager_dashboard')
@login_required
def manager_dashboard():
    if not current_user.is_manager:
        return redirect(url_for('main.index'))
    
    active_clients_count = Client.query.filter_by(status='Active').count()
    completed_tasks_count = Task.query.filter_by(status='Completed').count()
    assigned_tasks_count = Task.query.filter_by(status='Assigned').count()
    in_progress_tasks_count = Task.query.filter_by(status='In Progress').count()

    return render_template('manager_dashboard.html', 
                           active_clients_count=active_clients_count,
                           completed_tasks_count=completed_tasks_count,
                           assigned_tasks_count=assigned_tasks_count,
                           in_progress_tasks_count=in_progress_tasks_count)




@main.route('/worker_dashboard')
@login_required
def worker_dashboard():
    pending_tasks_count = Task.query.filter_by(worker_id=current_user.id, status='Assigned').count()
    in_progress_tasks_count = Task.query.filter_by(worker_id=current_user.id, status='In Progress').count()
    completed_tasks_count = Task.query.filter_by(worker_id=current_user.id, status='Completed').count()
    average_completion_time = db.session.query(db.func.avg(Task.completion_time)).filter_by(worker_id=current_user.id).scalar()
    return render_template('worker_dashboard.html', pending_tasks_count=pending_tasks_count, in_progress_tasks_count=in_progress_tasks_count, completed_tasks_count=completed_tasks_count, average_completion_time=average_completion_time) 

@main.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).order_by(Notification.timestamp.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@main.route('/mark_notification_as_read/<int:notification_id>')
@login_required
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.read = True
    db.session.commit()
    return redirect(url_for('main.notifications'))

@main.route('/clients')
@login_required
def clients():
    if current_user.is_manager:
        clients = Client.query.all()
    else:
        clients = Client.query.filter_by(user_id=current_user.id).all()
    return render_template('clients.html', clients=clients)

@main.route('/client/<int:client_id>')
@login_required
def client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    tasks = Task.query.filter_by(client_id=client_id).all()
    onboarding_tasks = OnboardingTask.query.filter_by(client_id=client_id).all()
    content_ideas = ContentIdea.query.filter_by(client_id=client_id).all()
    metrics = Metric.query.filter_by(client_id=client_id).all()
    return render_template('client_profile.html', client=client, tasks=tasks, onboarding_tasks=onboarding_tasks, content_ideas=content_ideas, metrics=metrics)


@main.route('/assign_task', methods=['GET', 'POST'])
@login_required
def assign_task():
    form = TaskForm()
    
    # Populate worker email dropdown with non-manager users
    form.worker_email.choices = [(user.email, user.email) for user in User.query.filter_by(is_manager=False).all()]
    
    # Populate client dropdown with clients
    form.client_id.choices = [(client.id, client.name) for client in Client.query.all()]

    if form.validate_on_submit():
        worker = User.query.filter_by(email=form.worker_email.data).first()
        if worker:
            new_task = Task(
                manager_id=current_user.id,
                worker_id=worker.id,
                client_id=form.client_id.data,
                task_description=form.task_description.data,
                deadline=form.deadline.data,
                status='Assigned'
            )
            db.session.add(new_task)
            db.session.commit()
            
            # Create notification for the worker
            notification = Notification(
                user_id=worker.id,
                message=f'You have been assigned a new task: {new_task.task_description}',
                type='task_assigned'
            )
            db.session.add(notification)
            
            # Create notification for managers
            managers = User.query.filter_by(is_manager=True).all()
            for manager in managers:
                notification = Notification(
                    user_id=manager.id,
                    message=f'A new task has been assigned to {worker.name}',
                    type='task_assigned'
                )
                db.session.add(notification)
                
            db.session.commit()
            
            flash('Task assigned successfully!', 'success')
            return redirect(url_for('main.kanban_board'))
        else:
            flash('Worker not found.', 'danger')
    return render_template('assign_task.html', form=form)



@main.route('/submit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def submit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskSubmissionForm()
    if form.validate_on_submit():
        task.status = 'Completed'
        task.completion_description = form.completion_description.data
        task.completion_link = form.completion_link.data
        task.completion_time = datetime.now()
        db.session.commit()
        
        # Create notification for the manager
        notification = Notification(
            user_id=task.manager_id,
            message=f'Task "{task.task_description}" has been completed by {task.worker.name}',
            type='task_completed'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Task submitted successfully!', 'success')
        return redirect(url_for('main.kanban_board'))
    return render_template('submit_task.html', form=form)


@main.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    form = ClientForm()
    if form.validate_on_submit():
        new_client = Client(
            user_id=current_user.id,
            name=form.name.data,
            contact_number=form.contact_number.data,
            business_category=form.business_category.data,
            social_media_handles=form.social_media_handles.data,
            goals=form.goals.data,
            specific_requests=form.specific_requests.data
        )
        db.session.add(new_client)
        db.session.commit()
        
        # Create notification for managers
        managers = User.query.filter_by(is_manager=True).all()
        for manager in managers:
            notification = Notification(
                user_id=manager.id,
                message=f'A new client "{new_client.name}" has been added by {current_user.name}',
                type='client_added'
            )
            db.session.add(notification)
        db.session.commit()
        
        flash('Client added successfully!', 'success')
        return redirect(url_for('main.clients'))
    return render_template('add_client.html', form=form)

@main.route('/add_onboarding_task/<int:client_id>', methods=['GET', 'POST'])
@login_required
def add_onboarding_task(client_id):
    form = OnboardingTaskForm()
    if form.validate_on_submit():
        new_task = OnboardingTask(
            client_id=client_id,
            task_name=form.task_name.data,
            responsible=form.responsible.data,
            deadline=form.deadline.data
        )
        db.session.add(new_task)
        db.session.commit()
        
        # Create notification for managers
        managers = User.query.filter_by(is_manager=True).all()
        for manager in managers:
            notification = Notification(
                user_id=manager.id,
                message=f'A new onboarding task "{new_task.task_name}" has been added for client ID {client_id}',
                type='onboarding_task_added'
            )
            db.session.add(notification)
        db.session.commit()
        
        flash('Onboarding task added successfully!', 'success')
        return redirect(url_for('main.client_profile', client_id=client_id))
    return render_template('add_onboarding_task.html', form=form)

@main.route('/add_content_idea/<int:client_id>', methods=['GET', 'POST'])
@login_required
def add_content_idea(client_id):
    form = ContentIdeaForm()
    if form.validate_on_submit():
        new_idea = ContentIdea(
            client_id=client_id,
            idea_source=form.idea_source.data,
            description=form.description.data,
            link=form.link.data,
            sound=form.sound.data,
            status=form.status.data
        )
        db.session.add(new_idea)
        db.session.commit()
        
        # Create notification for managers
        managers = User.query.filter_by(is_manager=True).all()
        for manager in managers:
            notification = Notification(
                user_id=manager.id,
                message=f'A new content idea has been added for client ID {client_id}',
                type='content_idea_added'
            )
            db.session.add(notification)
        db.session.commit()
        
        flash('Content idea added successfully!', 'success')
        return redirect(url_for('main.client_profile', client_id=client_id))
    return render_template('add_content_idea.html', form=form)

@main.route('/add_metric/<int:client_id>', methods=['GET', 'POST'])
@login_required
def add_metric(client_id):
    form = MetricForm()
    if form.validate_on_submit():
        new_metric = Metric(
            client_id=client_id,
            platform=form.platform.data,
            post_date=form.post_date.data,
            views=form.views.data,
            likes=form.likes.data,
            comments=form.comments.data,
            shares=form.shares.data
        )
        db.session.add(new_metric)
        db.session.commit()
        
        # Create notification for managers
        managers = User.query.filter_by(is_manager=True).all()
        for manager in managers:
            notification = Notification(
                user_id=manager.id,
                message=f'A new metric has been added for client ID {client_id}',
                type='metric_added'
            )
            db.session.add(notification)
        db.session.commit()
        
        flash('Metric added successfully!', 'success')
        return redirect(url_for('main.client_profile', client_id=client_id))
        return render_template('add_metric.html', form=form)
    
@main.route('/tasks', methods=['GET', 'POST'])
@login_required
def task_list():
    tasks = Task.query.filter_by(worker_id=current_user.id).all() if not current_user.is_manager else Task.query.all()
    form = TaskSubmissionForm()
    selected_task = None

    if request.method == 'POST' and form.validate_on_submit():
        selected_task = Task.query.get(form.task_id.data)
        if selected_task:
            selected_task.completion_description = form.completion_description.data
            selected_task.completion_link = form.completion_link.data
            selected_task.status = 'Completed'
            selected_task.completion_time = datetime.now()
            db.session.commit()
            flash('Task submitted successfully!', 'success')
            return redirect(url_for('main.task_list'))

    return render_template('task_list.html', tasks=tasks, is_worker=not current_user.is_manager, form=form, selected_task=selected_task)

from datetime import datetime, timezone


@main.route('/update_task_status', methods=['POST'])
@login_required
def update_task_status():
    data = request.get_json()
    task_id = data.get('task_id')
    new_status = data.get('status')
    task = Task.query.get(task_id)
    if task:
        if task.status != new_status:
            task.status = new_status
            if new_status == 'In Progress':
                task.in_progress_time = datetime.now(timezone.utc)
            elif new_status == 'Completed':
                task.completion_time = datetime.now(timezone.utc)
            db.session.commit()

            # Create notification for the manager
            worker_name = User.query.get(task.worker_id).name if task.worker_id else current_user.name
            notification_message = f'Task "{task.task_description}" has been moved to {new_status} by {worker_name}'
            notification = Notification(
                user_id=task.manager_id,
                message=notification_message,
                type='task_status_changed'
            )
            db.session.add(notification)
            db.session.commit()
            return jsonify({'message': f'Task status updated to {new_status}'})
        else:
            return jsonify({'message': 'Task status unchanged'}), 400
    else:
        return jsonify({'message': 'Task not found'}), 404

@main.route('/submitted_tasks_report')
@login_required
def submitted_tasks_report():
    tasks = Task.query.all()
    return render_template('submitted_tasks_report.html', tasks=tasks)


    tasks = Task.query.filter(Task.status == 'Completed').all()
    return render_template('submitted_tasks_report.html', tasks=tasks)



@main.route('/kanban_board')
@login_required
def kanban_board():
    if current_user.is_manager:
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(worker_id=current_user.id).all()
    return render_template('kanban_board.html', tasks=tasks)

@main.route('/submitted_tasks')
@login_required
def submitted_tasks():
    if current_user.is_manager:
        tasks = Task.query.filter_by(status='Completed').all()
    else:
        tasks = Task.query.filter_by(worker_id=current_user.id, status='Completed').all()
    return render_template('submitted_tasks.html', tasks=tasks)

@main.route('/forms')
@login_required
def forms():
    return render_template('forms.html')

import io
from flask import send_file
import csv

@main.route('/download_clients')
@login_required
def download_clients():
    clients = Client.query.all()
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8'))
    writer.writerow(['ID', 'Name', 'Contact Number', 'Business Category', 'Social Media Handles', 'Goals', 'Specific Requests'])
    for client in clients:
        writer.writerow([client.id, client.name, client.contact_number, client.business_category, client.social_media_handles, client.goals, client.specific_requests])
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='clients.csv', as_attachment=True)

@main.route('/download_tasks')
@login_required
def download_tasks():
    tasks = Task.query.all()
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8'))
    writer.writerow(['ID', 'Manager ID', 'Worker ID', 'Client ID', 'Task Description', 'Deadline', 'Status', 'Completion Description', 'Completion Link'])
    for task in tasks:
        writer.writerow([task.id, task.manager_id, task.worker_id, task.client_id, task.task_description, task.deadline, task.status, task.completion_description, task.completion_link])
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='tasks.csv', as_attachment=True)

@main.route('/download_onboarding_tasks/<int:client_id>')
@login_required
def download_onboarding_tasks(client_id):
    onboarding_tasks = OnboardingTask.query.filter_by(client_id=client_id).all()
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8'))
    writer.writerow(['ID', 'Task Name', 'Responsible', 'Deadline'])
    for task in onboarding_tasks:
        writer.writerow([task.id, task.task_name, task.responsible, task.deadline])
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='onboarding_tasks.csv', as_attachment=True)

@main.route('/download_content_ideas/<int:client_id>')
@login_required
def download_content_ideas(client_id):
    content_ideas = ContentIdea.query.filter_by(client_id=client_id).all()
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8'))
    writer.writerow(['ID', 'Idea Source', 'Description', 'Link', 'Sound', 'Status'])
    for idea in content_ideas:
        writer.writerow([idea.id, idea.idea_source, idea.description, idea.link, idea.sound, idea.status])
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='content_ideas.csv', as_attachment=True)

@main.route('/download_metrics/<int:client_id>')
@login_required
def download_metrics(client_id):
    metrics = Metric.query.filter_by(client_id=client_id).all()
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8'))
    writer.writerow(['ID', 'Platform', 'Post Date', 'Views', 'Likes', 'Comments', 'Shares'])
    for metric in metrics:
        writer.writerow([metric.id, metric.platform, metric.post_date, metric.views, metric.likes, metric.comments, metric.shares])
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='metrics.csv', as_attachment=True)






